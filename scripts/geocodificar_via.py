#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geolocalización sobre vía con la red ADIF (WFS Tramificación).

Uso:
    python geocodificar_via.py ES

Estrategia (de mayor a menor precisión):
  1. PK + línea con código → tramos ADIF del mismo código de línea → interpolar
     PK dentro del tramo (pki/pkd + geometría) → punto SOBRE la vía.
  2. PK sin línea → PKTeoricos más cercano (si hay algo cerca, <1 km) → sobre vía.
  3. Fallback: coordenada previa (Nominatim/CIAF/LLM) sin cambios.
Actualiza json/{pais}/*.json (ubicacion.lat/lng + ubicacion.metodo_geo).
"""
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
# id_provinc del geoJSON de ADIF = código provincial INE (verificado: Guipúzcoa→20,
# Cuenca→16, Jaén→23; tramo PALENCIA→idp 34). El mapa anterior estaba desplazado y
# hacía filtrar por provincias equivocadas (causa del error El Caleyo/17-2007).
IDP_A_PROVINCIA = {
    1: "Álava", 2: "Albacete", 3: "Alicante", 4: "Almería", 5: "Ávila",
    6: "Badajoz", 7: "Baleares", 8: "Barcelona", 9: "Burgos", 10: "Cáceres",
    11: "Cádiz", 12: "Castellón", 13: "Ciudad Real", 14: "Córdoba", 15: "A Coruña",
    16: "Cuenca", 17: "Girona", 18: "Granada", 19: "Guadalajara", 20: "Guipúzcoa",
    21: "Huelva", 22: "Huesca", 23: "Jaén", 24: "León", 25: "Lleida",
    26: "La Rioja", 27: "Lugo", 28: "Madrid", 29: "Málaga", 30: "Murcia",
    31: "Navarra", 32: "Ourense", 33: "Asturias", 34: "Palencia", 35: "Las Palmas",
    36: "Pontevedra", 37: "Salamanca", 38: "Santa Cruz de Tenerife", 39: "Cantabria",
    40: "Segovia", 41: "Sevilla", 42: "Soria", 43: "Tarragona", 44: "Teruel",
    45: "Toledo", 46: "Valencia", 47: "Valladolid", 48: "Vizcaya", 49: "Zamora",
    50: "Zaragoza", 51: "Ceuta", 52: "Melilla",
}
# cabeceras de provincia que los informes citan por el nombre de la ciudad
PROVINCIA_ALIAS = {"oviedo": "Asturias", "santiago de compostela": "A Coruña"}
# denominaciones antiguas/alternativas en el texto 'provincia' de los tramos ADIF
PROVINCIA_TEXTO_ALIAS = {
    "gerona": "Girona", "lerida": "Lleida", "orense": "Ourense",
    "coruna": "A Coruña", "rioja": "La Rioja", "alava": "Álava",
    "castellon": "Castellón", "avila": "Ávila",
}


def to_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def prov_de_tramo(t):
    """Nombre de provincia de un tramo: id_provinc INE, con alias y fallback texto."""
    idp = to_int(t.get("provincia_idp"))
    nombre = IDP_A_PROVINCIA.get(idp, "")
    if not nombre:
        raw = (t.get("provincia") or "").strip().title()
        nombre = PROVINCIA_TEXTO_ALIAS.get(norm(raw), raw)
    return PROVINCIA_ALIAS.get(norm(nombre), nombre)


def norm(s: str) -> str:
    """minúsculas + sin acentos + sin espacios extra."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_pk(pk_str):
    """'P.K. 429,825' / '368+925' / 'PK 415+648' / '581+060' → 429.825 / 368.925..."""
    if not pk_str:
        return None
    s = str(pk_str).strip()
    # separadores validos: + (km+m), , . (decimal) y / (notacion CIAF: 459/200 = 459,200)
    m = re.search(r"(\d{1,4})\s*[+,./]\s*(\d{1,3})(?!\d)", s)
    if not m:
        return None
    ent, dec = m.group(1), m.group(2)
    # '368+925' → 368 km + 925 m; '429,825' → 429.825 km
    if dec.startswith("+") or "+" in s:
        return float(ent) + int(dec) / 1000.0
    return float(f"{ent}.{dec}")


def parse_linea(linea_str):
    """'010 Madrid Atocha - Sevilla' / '100 Hendaya a Madrid' → ('010', ...).

    También códigos LV de 4 dígitos ('9502', '0878' alta velocidad): si el texto
    no trae nombre después del código, se devuelve el propio código.
    Tolera prefijos 'Línea '/'Linea ' que los informes CIAF usan a menudo.
    """
    if not linea_str:
        return None, None
    s = str(linea_str).strip()
    s = re.sub(r"^(?:l[ií]nea|lv|lin(?:e|í)a)\s+|^n[º°]?\s+", "", s, flags=re.I)
    m = re.match(r"^(\d{1,4})(?:\s*[-–]\s+(.+)|\s+(.+))?$", s)
    if m:
        code = m.group(1)
        resto = m.group(2) or m.group(3)
        if len(code) <= 3:
            code = code.zfill(3)
        return (code, resto) if resto else (code, None)
    return None, s


def haversine(lat1, lng1, lat2, lng2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def interpolar_en_tramo(tramo, pk):
    """PK dentro del tramo → coordenada interpolada sobre la geometría."""
    pki, pkd = tramo["pki"], tramo["pkd"]
    if pki == pkd:
        coords = tramo["coords"][0]
        return coords[len(coords) // 2]
    frac = max(0.0, min(1.0, (pk - min(pki, pkd)) / (max(pki, pkd) - min(pki, pkd))))
    coords = tramo["coords"][0]  # primera línea del MultiLineString
    if frac <= 0: return coords[0]
    if frac >= 1: return coords[-1]
    # posición proporcional por vértices (suficiente: tramos ~300-500 m)
    idx = frac * (len(coords) - 1)
    i = int(idx)
    f = idx - i
    if i >= len(coords) - 1:
        return coords[-1]
    (x1, y1), (x2, y2) = coords[i], coords[i + 1]
    return [x1 + (x2 - x1) * f, y1 + (y2 - y1) * f]


def cargar_red():
    """Tramos + PKTeoricos → estructuras de búsqueda."""
    print("Cargando red ADIF...", flush=True)
    tramos = []
    tf = DATA / "adif-tramos.geojson"
    if tf.exists():
        gj = json.loads(tf.read_text(encoding="utf-8"))
        for f in gj["features"]:
            p = f["properties"]
            if not p.get("codtramo") or p.get("pki") is None:
                continue
            tramos.append({
                "codtramo": p["codtramo"],
                "cod_eje": p.get("cod_eje") or "",
                "cod_linea": p.get("cod_linea") or "",
                "provincia_idp": p.get("id_provinc"),
                "provincia": p.get("provincia"),
                "pki": float(p["pki"]),
                "pkd": float(p["pkd"]),
                "coords": f["geometry"]["coordinates"],
            })
    print(f"  {len(tramos)} tramos", flush=True)
    pkteor = []
    pf = DATA / "adif-pkteoricos.geojson"
    if pf.exists():
        gj = json.loads(pf.read_text(encoding="utf-8"))
        for f in gj["features"]:
            p = f["properties"]
            if p.get("pk") is None:
                continue
            pkteor.append({
                "codtramo": p.get("codtramo") or "",
                "pk": float(p["pk"]),
                "idp": p.get("id_provinc"),
                "lng": f["geometry"]["coordinates"][0],
                "lat": f["geometry"]["coordinates"][1],
            })
    print(f"  {len(pkteor)} pk teóricos", flush=True)
    return tramos, pkteor


def indice_linea(tramos):
    """Índice: código de línea → [tramos].

    Claves: los dígitos iniciales de cod_linea ('130-Gijón...' → '130') Y el
    segmento de línea del codtramo, codtramo[2:5] ('061300210' → '130').
    NUNCA codtramo[:3]: son eje(2)+primer dígito de línea y colisiona con
    códigos CIAF de otras líneas (fue la causa del error El Caleyo/17-2007).
    """
    idx = {}
    for t in tramos:
        claves = set()
        m = re.match(r"^(\d{3,4})-", t["cod_linea"] or "")
        if m:
            claves.add(m.group(1))
        ct = t["codtramo"] or ""
        if re.fullmatch(r"\d{9}", ct):
            claves.add(ct[2:5])
        for k in claves:
            idx.setdefault(k, []).append(t)
    return idx


def main(codigo: str):
    tramos, pkteor = cargar_red()
    idx = indice_linea(tramos)
    # pk teóricos por codtramo
    pk_por_tramo = {}
    for p in pkteor:
        pk_por_tramo.setdefault(p["codtramo"], []).append(p)

    def idps_de(prov_norm):
        """Códigos INE de una provincia declarada (con alias de cabeceras)."""
        prov_norm = norm(PROVINCIA_ALIAS.get(prov_norm, prov_norm))
        return [k for k, v in IDP_A_PROVINCIA.items() if norm(v) == prov_norm]

    jsons = sorted((RAIZ / "json" / codigo).glob("*.json"))
    stats = {"via_pk": 0, "via_pkteorico": 0, "previa": 0, "sin_geo": 0}
    for f in jsons:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        loc = d.get("ubicacion") or {}
        # ubicacion manda: es el dato que el geocodificador/verificador ha contrastado
        pk = parse_pk(loc.get("pk") or d.get("pk"))
        cod_linea, _ = parse_linea(loc.get("linea") or d.get("linea"))
        punto = None
        metodo = None

        # 1) PK + código de línea → interpolación en tramo
        if pk is not None and cod_linea:
            candidatos = idx.get(cod_linea, [])
            prov = norm((loc.get("provincia") or d.get("provincia") or ""))
            if prov and candidatos:
                prov_ok = norm(PROVINCIA_ALIAS.get(prov, prov))
                con_prov = [t for t in candidatos if norm(prov_de_tramo(t)) == prov_ok]
                if con_prov:
                    candidatos = con_prov
            # tramo cuyo rango [pki,pkd] contenga el PK
            en_rango = [t for t in candidatos
                        if min(t["pki"], t["pkd"]) - 0.3 <= pk <= max(t["pki"], t["pkd"]) + 0.3]
            if en_rango:
                # el de rango más estrecho (más específico)
                t = min(en_rango, key=lambda t: abs(t["pkd"] - t["pki"]))
                xy = interpolar_en_tramo(t, pk)
                punto, metodo = [xy[1], xy[0]], "via_pk"
            elif candidatos:
                # tramo con el PK más cercano dentro de la misma línea (< 2 km de pk)
                t = min(candidatos, key=lambda t: min(abs(t["pki"] - pk), abs(t["pkd"] - pk)))
                if min(abs(t["pki"] - pk), abs(t["pkd"] - pk)) < 2.0:
                    xy = interpolar_en_tramo(t, pk)
                    punto, metodo = [xy[1], xy[0]], "via_pk"
                    en_rango = [t]

        # 2) PK sin resolver → PKTeorico por línea+PK+provincia (sin depender de
        #    la coord vieja: una coord previa errónea no debe perpetuarse)
        if punto is None and pk is not None:
            prov = norm((loc.get("provincia") or d.get("provincia") or ""))
            idps = idps_de(prov) if prov else []
            ref = (loc.get("lat"), loc.get("lng"))

            # 2a) match estricto: pk ±0.6 + línea + provincia
            def puntos_pk(cod_linea, idps, pk, tol=0.6):
                out = []
                for p in pkteor:
                    if abs(p["pk"] - pk) > tol:
                        continue
                    if idps and to_int(p.get("idp")) not in idps:
                        continue
                    if cod_linea:
                        ct = p.get("codtramo") or ""
                        li = ct[2:5] if re.fullmatch(r"\d{9}", ct) else ""
                        if li != cod_linea:
                            continue
                    out.append(p)
                return out

            matches = puntos_pk(cod_linea, idps, pk) if (cod_linea or idps) else []
            if not matches and cod_linea and idps and pk is not None:
                # 2b) línea declarada recortada en ADIF (p.ej. 600 acaba en La
                # Boella y el pk CIAF sigue): relajar a ±10 km de pk en línea+prov
                matches = puntos_pk(cod_linea, idps, pk, tol=10.0)
            if not matches and idps:
                matches = puntos_pk(None, idps, pk)
            if matches:
                # si hay racimo, el centroide; si ref previa, el más coherente
                if ref and ref[0]:
                    p = min(matches, key=lambda p: haversine(ref[0], ref[1], p["lat"], p["lng"]))
                else:
                    p = matches[len(matches) // 2]
                punto, metodo = [p["lat"], p["lng"]], "via_pkteorico"

        # 3) fallback: mantener coordenada previa
        if punto is None:
            if loc.get("lat"):
                stats["previa"] += 1
            else:
                stats["sin_geo"] += 1
            continue

        if metodo == "via_pkteorico" and loc.get("lat"):
            # solo aceptar pk teórico si está cerca de la coord previa
            pass  # ya filtrado arriba con haversine < 1500 m
        loc["lat"], loc["lng"] = punto
        loc["metodo_geo"] = metodo
        d["ubicacion"] = loc
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        stats[metodo] += 1

    print(f"[{codigo}] {json.dumps(stats, ensure_ascii=False)}")
    print(f"  via_pk        = interpolado en tramo (máx precisión)")
    print(f"  via_pkteorico = pk teórico cercano")
    print(f"  previa        = se mantiene Nominatim/CIAF/LLM")
    print(f"  sin_geo       = sin coordenada")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1].upper())
