# -*- coding: utf-8 -*-
"""
Geocodificacion por ESTACION: para informes sin PK casable pero con estacion
conocida, busca la estacion en el dataset IGN (RedFerrocarrilesIGN, CC-BY 4.0).

Estrategia:
  1. normaliza nombres (sin acentos, minusculas, sin "estacion de/apeadero de")
  2. coincidencia exacta -> si hay varias, la mas cercana a la provincia del informe
  3. si no, coincidencia por contencion (nombre de estacion contiene al del informe)

Escribe metodo_geo = "estacion_ign".
Uso: python geocodificar_estacion.py ES
"""
import glob
import json
import math
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVINCIAS = {
    "alava": "01", "albacete": "02", "alicante": "03", "almeria": "04",
    "avila": "05", "badajoz": "06", "baleares": "07", "barcelona": "08",
    "burgos": "09", "caceres": "10", "cadiz": "11", "castellon": "12",
    "ciudad real": "13", "cordoba": "14", "a coruna": "15", "cuenca": "16",
    "girona": "17", "granada": "18", "guadalajara": "19", "guipuzcoa": "20",
    "huelva": "21", "huesca": "22", "jaen": "23", "leon": "24", "lleida": "25",
    "la rioja": "26", "lugo": "27", "madrid": "28", "malaga": "29", "murcia": "30",
    "navarra": "31", "ourense": "32", "asturias": "33", "palencia": "34",
    "las palmas": "35", "pontevedra": "36", "salamanca": "37",
    "santa cruz de tenerife": "38", "cantabria": "39", "segovia": "40",
    "sevilla": "41", "soria": "42", "tarragona": "43", "teruel": "44",
    "toledo": "45", "valencia": "46", "valladolid": "47", "vizcaya": "48",
    "zamora": "49", "zaragoza": "50", "ceuta": "51", "melilla": "52",
}


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFD", str(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"\b(estacion|de|del|la|el|apeadero|ferrocarril)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def distancia_m(lat1, lng1, lat2, lng2):
    y = (lat2 - lat1) * 111_320.0
    x = (lng2 - lng1) * 111_320.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(x, y)


def centroides_provincial():
    """Centroide (lat,lng) de la red de PK teóricos por código INE de provincia.

    Da referencia geográfica para desambiguar estaciones con el mismo nombre
    en distintas provincias (el dataset IGN no trae id_prov).
    """
    p = os.path.join(RAIZ, "data", "adif-pkteoricos.geojson")
    if not os.path.exists(p):
        return {}
    gj = json.load(open(p, encoding="utf-8"))
    acc = {}
    for feat in gj.get("features", []):
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates")
        idp = str(props.get("id_provinc") or "").strip().zfill(2)
        if not coords or idp in ("", "00"):
            continue
        x, y = coords[0], coords[1]
        s = acc.setdefault(idp, [0.0, 0.0, 0])
        s[0] += y
        s[1] += x
        s[2] += 1
    return {k: (v[0] / v[2], v[1] / v[2]) for k, v in acc.items() if v[2]}


def main():
    codigo = sys.argv[1] if len(sys.argv) > 1 else "ES"

    # cargar estaciones IGN (dataset RedFerrocarrilesIGN, CC-BY 4.0) — versionado
    # en data/ para que el script sea reproducible (antes vivía en Temp/ y se perdía)
    estaciones = []
    rutas = sorted(glob.glob(os.path.join(RAIZ, "data", "ign-estaciones*.json")))
    if not rutas:
        print("[EST] ERROR: faltan data/ign-estaciones*.json")
        return
    for p in rutas:
        datos = json.load(open(p, encoding="utf-8"))
        for feat in datos.get("features", []):
            a = feat.get("attributes") or {}
            g = feat.get("geometry") or {}
            if not a.get("nombre") or "x" not in g:
                continue
            estaciones.append({
                "nombre": a["nombre"],
                "norm": normalizar(a["nombre"]),
                "lat": g["y"], "lng": g["x"],
                "tipo": a.get("tipo_estfd", ""),
            })
    print(f"[EST] {len(estaciones)} estaciones IGN cargadas")
    centros = centroides_provincial()
    print(f"[EST] {len(centros)} centroides provinciales (ADIF)")

    jsons = sorted(glob.glob(os.path.join(RAIZ, "json", codigo, "*.json")))
    hechos = 0
    for jf in jsons:
        d = json.load(open(jf, encoding="utf-8"))
        loc = d.get("ubicacion") or {}
        if loc.get("lat") or d.get("lat"):
            continue  # ya geolocalizado
        est = d.get("estacion") or loc.get("estacion")
        if not est:
            continue
        # limpiar prefijos del informe
        n_est = normalizar(est)
        if len(n_est) < 4:
            continue
        provincia = (d.get("provincia") or loc.get("provincia") or "").lower()
        cod_prov = PROVINCIAS.get(normalizar(provincia))

        # 1) exacta
        candidatos = [e for e in estaciones if e["norm"] == n_est]
        # 2) contencion de PALABRA COMPLETA (evita "leon" dentro de "pueblo de san abria")
        if not candidatos:
            palabras = [p for p in n_est.split() if len(p) >= 4]
            candidatos = [e for e in estaciones
                          if palabras and all(p in e["norm"].split() for p in palabras)]
        if not candidatos:
            continue
        # desempate: el candidato más cercano al centroide de la red ADIF de la
        # provincia del informe (a >120 km se considera otra provincia: descartar)
        if len(candidatos) > 1 and cod_prov and cod_prov in centros:
            cLat, cLng = centros[cod_prov]
            cerca = [e for e in candidatos
                     if distancia_m(cLat, cLng, e["lat"], e["lng"]) <= 120_000]
            if cerca:
                candidatos = cerca
        # si tras desempate hay varios, ABSTENERSE (no inventar)
        if len(candidatos) != 1:
            continue
        e = candidatos[0]
        loc["lat"], loc["lng"] = e["lat"], e["lng"]
        loc["metodo_geo"] = "estacion_ign"
        loc["estacion_ign"] = e["nombre"]
        d["ubicacion"] = loc
        json.dump(d, open(jf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        hechos += 1

    print(f"[EST] geocodificados por estacion: {hechos}")


if __name__ == "__main__":
    main()
