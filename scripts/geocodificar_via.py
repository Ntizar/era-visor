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
IDP_A_PROVINCIA = {
    1: "Álava", 2: "Albacete", 3: "Alicante", 4: "Almería", 5: "Ávila",
    6: "Badajoz", 7: "Baleares", 8: "Barcelona", 9: "Burgos", 10: "Burgos",
    11: "Cáceres", 12: "Cáceres", 13: "Cádiz", 14: "Córdoba", 15: "A Coruña",
    16: "A Coruña", 17: "Girona", 18: "Gipuzkoa", 19: "Huelva", 20: "Huesca",
    21: "Jaén", 22: "La Rioja", 23: "León", 24: "León", 25: "Lleida",
    26: "La Rioja", 27: "Lugo", 28: "Madrid", 29: "Málaga", 30: "Murcia",
    31: "Navarra", 32: "Ourense", 33: "Asturias", 34: "Asturias", 35: "Castellón",
    36: "Las Palmas", 37: "Cantabria", 38: "Cantabria", 43: "Huesca", 44: "Teruel",
    45: "Guadalajara", 47: "Valladolid", 49: "Zamora", 50: "Zaragoza",
    51: "Cáceres", 52: "Ceuta", 53: "Melilla", 54: "Madrid", 55: "Madrid",
    56: "Madrid", 57: "Madrid", 58: "Sevilla", 59: "Alicante", 60: "Santa Cruz de Tenerife",
    61: "Almería", 62: "Las Palmas", 66: "Zaragoza", 67: "Zaragoza",
}


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
    m = re.search(r"(\d{1,4})\s*[+,\.]\s*(\d{1,3})\s*$", s)
    if not m:
        m = re.search(r"(\d{1,4})[.,](\d{1,3})", s)
        if not m:
            return None
    ent, dec = m.group(1), m.group(2)
    # '368+925' → 368 km + 925 m; '429,825' → 429.825 km
    if dec.startswith("+") or "+" in s:
        return float(ent) + int(dec) / 1000.0
    return float(f"{ent}.{dec}")


def parse_linea(linea_str):
    """'010 Madrid Atocha - Sevilla' / '100 Hendaya a Madrid' → ('010', 'madrid atocha sevilla')."""
    if not linea_str:
        return None, None
    s = str(linea_str).strip()
    m = re.match(r"^(\d{1,3})\s+(.+)$", s)
    if m:
        return m.group(1).zfill(3), m.group(2)
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


def indice_eje(tramos):
    """Índice: código de línea (3 dígitos, de cod_linea o cod_eje) → [tramos]."""
    idx = {}
    for t in tramos:
        m = re.match(r"^(\d{3})-", t["cod_linea"] or "")
        eje = m.group(1) if m else None
        if not eje:
            # cod_eje: '01-Madrid Chamartín - Irun' → 01 no es código de línea CIAF;
            # el código CIAF de 3 dígitos suele coincidir con los primeros 3 del codtramo
            eje = (t["codtramo"] or "")[:3]
        idx.setdefault(eje, []).append(t)
    return idx


def main(codigo: str):
    tramos, pkteor = cargar_red()
    idx = indice_eje(tramos)
    # pk teóricos por codtramo
    pk_por_tramo = {}
    for p in pkteor:
        pk_por_tramo.setdefault(p["codtramo"], []).append(p)

    jsons = sorted((RAIZ / "json" / codigo).glob("*.json"))
    stats = {"via_pk": 0, "via_pkteorico": 0, "previa": 0, "sin_geo": 0}
    for f in jsons:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        loc = d.get("ubicacion") or {}
        pk = parse_pk(d.get("pk") or loc.get("pk"))
        cod_linea, _ = parse_linea(d.get("linea") or loc.get("linea"))
        punto = None
        metodo = None

        # 1) PK + código de línea → interpolación en tramo
        if pk is not None and cod_linea:
            candidatos = idx.get(cod_linea, [])
            # filtrar por provincia si la conocemos (desambigua líneas largas)
            prov = norm((loc.get("provincia") or d.get("provincia") or ""))
            if prov and candidatos:
                def en_prov(t):
                    idp = t.get("provincia_idp")
                    nombre = IDP_A_PROVINCIA.get(idp, "") or (t.get("provincia") or "")
                    return norm(nombre) == prov
                con_prov = [t for t in candidatos if en_prov(t)]
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

        # 2) PK sin línea → PKTeorico más cercano por codtramo+pk
        if punto is None and pk is not None:
            # probar tramos cuyo codtramo empieza igual que... no hay pista; buscar
            # global: pk teóricos con mismo valor pk y cerca de la provincia del informe
            prov = norm((loc.get("provincia") or d.get("provincia") or ""))
            idps = [k for k, v in IDP_A_PROVINCIA.items() if norm(v) == prov] if prov else []
            ref = (loc.get("lat"), loc.get("lng"))
            mejor, mejor_d = None, 1e9
            for p in pkteor:
                if abs(p["pk"] - pk) > 0.6:
                    continue
                if idps and p["idp"] not in idps:
                    continue
                if ref and ref[0]:
                    dd = haversine(ref[0], ref[1], p["lat"], p["lng"])
                else:
                    # sin referencia: coste = |pk diff| * 1000 (heurística)
                    dd = abs(p["pk"] - pk) * 1000
                if dd < mejor_d:
                    mejor, mejor_d = p, dd
            if mejor and (ref and mejor_d < 1500 or not ref):
                punto, metodo = [mejor["lat"], mejor["lng"]], "via_pkteorico"

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
