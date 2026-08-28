# -*- coding: utf-8 -*-
"""
Revisor de localización de informes contra la red ferroviaria ADIF real.

Para cada informe geolocalizado:
  1. Distancia al punto kilométrico ADIF más cercano (proxy de distancia a vía).
  2. Provincia del PK más cercano vs provincia declarada en el informe.

Salida: data/revision/{PAIS}-localizacion.json + resumen en consola.
Uso: python revisar_localizacion.py ES
"""
import json
import math
import os
import sys
import unicodedata

CODIGO = sys.argv[1] if len(sys.argv) > 1 else "ES"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# INE: código de provincia -> nombre
PROVINCIAS_INE = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería",
    "05": "Ávila", "06": "Badajoz", "07": "Baleares", "08": "Barcelona",
    "09": "Burgos", "10": "Cáceres", "11": "Cádiz", "12": "Castellón",
    "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña", "16": "Cuenca",
    "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Guipúzcoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León",
    "25": "Lleida", "26": "La Rioja", "27": "Lugo", "28": "Madrid",
    "29": "Málaga", "30": "Murcia", "31": "Navarra", "32": "Ourense",
    "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
    "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife",
    "39": "Cantabria", "40": "Segovia", "41": "Sevilla", "42": "Soria",
    "43": "Tarragona", "44": "Teruel", "45": "Toledo", "46": "Valencia",
    "47": "Valladolid", "48": "Vizcaya", "49": "Zamora", "50": "Zaragoza",
    "51": "Ceuta", "52": "Melilla",
}

# Umbrales en metros
OK_VIA = 500          # < 500 m del PK más cercano: bien ubicado
DUDA_VIA = 2000       # 500-2000 m: revisar; > 2000 m: mal ubicado


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFD", str(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t


def coinciden_provincia(declarada, ine):
    """True si la provincia declarada coincide (o es compatible) con la INE."""
    if not declarada or not ine:
        return None  # no comparable
    a, b = normalizar(declarada), normalizar(PROVINCIAS_INE.get(ine, ine))
    if not a or not b:
        return None
    return a in b or b in a


def distancia_m(lat1, lng1, lat2, lng2):
    """Distancia aproximada en metros (plana, válida a escala nacional)."""
    y = (lat2 - lat1) * 111_320.0
    x = (lng2 - lng1) * 111_320.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(x, y)


def main():
    ruta_db = os.path.join(RAIZ, "data", "db", "reports", f"{CODIGO}.json")
    ruta_pk = os.path.join(RAIZ, "data", "adif-pkteoricos.geojson")

    with open(ruta_db, encoding="utf-8") as f:
        informes = json.load(f)
    with open(ruta_pk, encoding="utf-8") as f:
        pk_datos = json.load(f)

    # Puntos PK precalcados
    puntos = []
    for feat in pk_datos["features"]:
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates")
        if not coords or len(coords) != 2:
            continue
        puntos.append({
            "lat": float(coords[1]),
            "lng": float(coords[0]),
            "pk": props.get("pk"),
            "codtramo": props.get("codtramo"),
            "provincia": str(props.get("id_provinc") or "").zfill(2),
        })
    print(f"[REV] {len(informes)} informes | {len(puntos)} puntos PK ADIF")

    revision = []
    conteo = {"bien": 0, "duda": 0, "mal": 0, "sin_coords": 0,
              "provincia_ok": 0, "provincia_mal": 0, "provincia_nd": 0}

    for r in informes:
        lat, lng = r.get("lat"), r.get("lng")
        entrada = {
            "id": r["id"], "titulo": (r.get("titulo") or "")[:90],
            "provincia": r.get("provincia"), "pk": r.get("pk"),
            "linea": r.get("linea"), "lat": lat, "lng": lng,
            "metodo": r.get("metodo_geo") or r.get("fuente_geo"),
        }
        if lat is None or lng is None:
            entrada["veredicto"] = "sin_coords"
            conteo["sin_coords"] += 1
            revision.append(entrada)
            continue

        # PK más cercano (barrido simple; 300 x 17k es asumible)
        mejor, mejor_d = None, 1e18
        for p in puntos:
            d = distancia_m(lat, lng, p["lat"], p["lng"])
            if d < mejor_d:
                mejor_d, mejor = d, p

        entrada["dist_via_m"] = round(mejor_d)
        entrada["pk_cercano"] = mejor["pk"]
        entrada["provincia_ine"] = PROVINCIAS_INE.get(mejor["provincia"], mejor["provincia"])
        entrada["coord_pkcercano"] = [mejor["lat"], mejor["lng"]]
        entrada["codtramo_cercano"] = mejor["codtramo"]

        if mejor_d <= OK_VIA:
            entrada["veredicto"] = "bien"
            conteo["bien"] += 1
        elif mejor_d <= DUDA_VIA:
            entrada["veredicto"] = "duda"
            conteo["duda"] += 1
        else:
            entrada["veredicto"] = "mal"
            conteo["mal"] += 1

        eq = coinciden_provincia(r.get("provincia"), mejor["provincia"])
        if eq is True:
            entrada["provincia_ok"] = True
            conteo["provincia_ok"] += 1
        elif eq is False:
            entrada["provincia_ok"] = False
            conteo["provincia_mal"] += 1
        else:
            entrada["provincia_ok"] = None
            conteo["provincia_nd"] += 1
        revision.append(entrada)

    # Informes con provincia declarada pero SIN coords: no comprobables aquí,
    # se listan para el revisor IA.
    os.makedirs(os.path.join(RAIZ, "data", "revision"), exist_ok=True)
    ruta_sal = os.path.join(RAIZ, "data", "revision", f"{CODIGO}-localizacion.json")
    with open(ruta_sal, "w", encoding="utf-8") as f:
        json.dump(revision, f, ensure_ascii=False, indent=1)

    print(f"[REV] Veredictos: bien={conteo['bien']} duda={conteo['duda']} "
          f"mal={conteo['mal']} sin_coords={conteo['sin_coords']}")
    print(f"[REV] Provincia: ok={conteo['provincia_ok']} mal={conteo['provincia_mal']} "
          f"no_comparable={conteo['provincia_nd']}")
    print(f"[REV] Detalle -> {ruta_sal}")

    # Top 15 mal ubicados para acción inmediata
    peores = [e for e in revision if e.get("veredicto") == "mal"]
    peores.sort(key=lambda e: -e.get("dist_via_m", 0))
    if peores:
        print("\n[REV] PEORES 15:")
        for e in peores[:15]:
            print(f"  {e['dist_via_m']:>7} m | {e['provincia'] or '—':<16} | "
                  f"pk={e.get('pk') or '—':<14} | {e['titulo'][:60]}")


if __name__ == "__main__":
    main()
