#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scraping del listado de informes de ERA (era.europa.eu) por país.

Uso:
    python scrape_pais.py ES [DE ...]

Descubre las páginas de año de cada país y extrae los enlaces a PDFs.
Guarda: data/pdf-manifest/<PAIS>.json  →  lista de
    {"pdf": "/system/files/...", "year": 2023, "title": "...", "country": "ES"}
"""
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE = "https://www.era.europa.eu"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "pdf-manifest"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# slug de país → código del proyecto
SLUGS = {
    "ES": "es-investigations", "AT": "at-investigations", "BE": "be-investigations",
    "BG": "bg-investigations", "CH": "ch-investigations", "CZ": "cz-investigations",
    "DE": "de-investigations", "DK": "dk-investigations", "EE": "ee-investigations",
    "EL": "el-investigations", "FI": "fi-investigations", "FR": "fr-investigations",
    "HR": "hr-investigations", "HU": "hu-investigations", "IE": "ie-investigations",
    "IT": "it-investigations", "LT": "lt-investigations", "LU": "lu-investigations",
    "LV": "lv-investigations", "NL": "nl-investigations", "NO": "no-investigations",
    "PL": "pl-investigations", "PT": "pt-investigations", "RO": "ro-investigations",
    "RS": "serbia-investigations", "SE": "se-investigations", "SI": "si-investigations",
    "SK": "sk-investigations", "UK": "uk-investigations",
}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def extraer_pdfs(html: str) -> list[dict]:
    """Extrae enlaces a PDFs del bloque principal de una página de año."""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    main = m.group(1) if m else html
    out = []
    for mm in re.finditer(r'<a[^>]+href="(/system/files/[^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', main, re.S | re.I):
        href = mm.group(1).split("?")[0]
        texto = re.sub(r"<[^>]+>", " ", mm.group(2))
        texto = re.sub(r"\s+", " ", texto).strip()
        out.append({"pdf": href})
    # fallback: enlaces sueltos sin texto, rutas /system/files/ y /sites/default/files/
    if not out:
        for mm in re.finditer(r'href="(/(?:system/files|sites/default/files)/[^"]+\.pdf[^"]*)"', main, re.I):
            out.append({"pdf": mm.group(1).split("?")[0]})
    return out


def scrape_pais(code: str) -> list[dict]:
    slug = SLUGS[code]
    idx_url = f"{BASE}/era-folder/{slug}"
    html = get(idx_url)
    main = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    main = main.group(1) if main else html
    # páginas de año: href="/era-folder/2006-5" >2006<
    anios = re.findall(r'href="(/era-folder/[^"]+)"[^>]*>(\d{4})<', main)
    if not anios:
        anios = [(idx_url.replace(BASE, ""), "")]
        print(f"  ⚠ {code}: sin páginas de año, probando la propia página índice")
    registros = []
    vistos = set()
    for ruta, anio in anios:
        url = BASE + ruta
        try:
            h = get(url)
        except Exception as e:
            print(f"  ✗ {code} {anio}: {e}")
            continue
        for item in extraer_pdfs(h):
            if item["pdf"] in vistos:
                continue
            vistos.add(item["pdf"])
            item["year"] = int(anio) if anio else None
            item["country"] = code
            registros.append(item)
        time.sleep(0.4)
    return registros


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for code in [a.upper() for a in sys.argv[1:]]:
        if code not in SLUGS:
            print(f"País no soportado: {code}")
            continue
        print(f"[{code}] Scrapeando...")
        registros = scrape_pais(code)
        dest = OUT_DIR / f"{code}.json"
        dest.write_text(json.dumps(registros, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  ✓ {code}: {len(registros)} PDFs → {dest}")


if __name__ == "__main__":
    main()
