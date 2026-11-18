#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga de PDFs del manifest de un país (reanudable).

Uso:
    python descargar_pdfs.py ES

Lee data/pdf-manifest/ES.json y descarga a pdfs/ES/. Salta los ya descargados.
"""
import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE = "https://www.era.europa.eu"
# ERA responde 429 si el UA no parece un navegador de verdad: hacen falta UA completo,
# Accept y Referer. Con estas cabeceras los PDF bajan a ~0,5 s cada uno, sin límite.
UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/pdf,text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}
RAIZ = Path(__file__).resolve().parent.parent


def descargar(codigo: str):
    cabeceras = dict(UA, Referer=f"{BASE}/era-folder/{codigo.lower()}-investigations")
    manifest = json.loads((RAIZ / "data" / "pdf-manifest" / f"{codigo}.json").read_text(encoding="utf-8"))
    dest_dir = RAIZ / "pdfs" / codigo
    dest_dir.mkdir(parents=True, exist_ok=True)
    ok, fail = 0, 0
    for i, item in enumerate(manifest):
        ruta = item["pdf"]
        nombre = urllib.parse.unquote(ruta.split("/")[-1])
        dest = dest_dir / nombre
        if dest.exists() and dest.stat().st_size > 0:
            ok += 1
            continue
        url = BASE + ruta
        datos = None
        for intento in range(6):
            try:
                req = urllib.request.Request(url, headers=cabeceras)
                with urllib.request.urlopen(req, timeout=120) as r:
                    datos = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    pausa = 20 * (intento + 1)
                    print(f"  ⏳ 429 en {nombre[:50]} — espero {pausa}s (intento {intento + 1}/6)")
                    time.sleep(pausa)
                else:
                    print(f"  ✗ {nombre[:60]}: HTTP {e.code}")
                    break
            except Exception as e:
                print(f"  ✗ {nombre[:60]}: {e}")
                break
        if datos:
            dest.write_bytes(datos)
            ok += 1
            if ok % 25 == 0:
                print(f"  [{codigo}] {ok}/{len(manifest)} descargados")
        else:
            fail += 1
        time.sleep(1.2)  # cortesía mínima con ERA (los PDF los sirve su CDN: ~0,4 s)
    print(f"[{codigo}] LISTO: {ok} descargados, {fail} fallos, total manifest {len(manifest)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    descargar(sys.argv[1].upper())
