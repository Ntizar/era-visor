#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geocodificación de json/ES/*.json con Nominatim + caché local.

Uso:
    python geocodificar.py ES

Prioridad: caché (data/db/coords-cache.json) → Nominatim (1 req/s, UA sin paréntesis).
Estrategias por registro: estación+provincia → estación → provincia → ubicación eRAIL.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "era-visor-geocoder/1.0"}  # sin paréntesis: Nominatim rechaza UAs con ()
CACHE = RAIZ / "data" / "db" / "coords-cache.json"
CACHE.parent.mkdir(parents=True, exist_ok=True)


def cargar_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def nominatim(query: str):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 3, "countrycodes": "es"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        datos = json.loads(r.read().decode())
    # priorizar resultados ferroviarios
    mejor = None
    for d in datos:
        if d.get("class") == "railway" or "station" in d.get("type", ""):
            mejor = d
            break
    if not mejor and datos:
        mejor = datos[0]
    if not mejor:
        return None, None
    return float(mejor["lat"]), float(mejor["lon"])


def geocodificar(codigo: str):
    cache = cargar_cache()
    jsons = sorted((RAIZ / "json" / codigo).glob("*.json"))
    nuevos = 0
    for f in jsons:
        d = json.loads(f.read_text(encoding="utf-8"))
        loc = d.get("ubicacion") or {}
        if loc.get("lat") and loc.get("lng"):
            continue
        est = (loc.get("estacion") or "").strip()
        prov = (loc.get("provincia") or "").strip()
        nombre_archivo = f.stem
        claves = [k for k in (f"{est} {prov}", est, prov) if k]
        # añadir ubicación eRAIL como último recurso
        erail_loc = (d.get("erail") or {}).get("Location name") or ""
        if erail_loc:
            claves.append(erail_loc)
        coords = None
        for clave in claves:
            k = clave.strip().lower()
            if k in cache:
                coords = cache[k]
                if coords:
                    break
                continue  # cacheada como None → siguiente estrategia
            try:
                lat, lng = nominatim(clave)
            except Exception as e:
                print(f"  ⚠ {clave}: {e}")
                time.sleep(5)
                lat, lng = None, None
            cache[k] = [lat, lng]
            coords = (lat, lng)
            nuevos += 1
            time.sleep(1.1)  # ToS Nominatim
            if coords:
                break
        if coords:
            loc["lat"], loc["lng"] = coords
            d["ubicacion"] = loc
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    geolocalizados = sum(
        1 for f in jsons
        if (json.loads(f.read_text(encoding="utf-8")).get("ubicacion") or {}).get("lat"))
    print(f"[{codigo}] {geolocalizados}/{len(jsons)} geolocalizados ({nuevos} queries nuevas)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    geocodificar(sys.argv[1].upper())
