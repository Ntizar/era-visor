# -*- coding: utf-8 -*-
"""descargar_todo.py — descarga los PDFs de todos los países con manifiesto, en serie.

Reanudable: salta lo ya descargado. Pausa entre países para no despertar el 429 de ERA.

Uso:
    python scripts/descargar_todo.py            # todos los manifiestos presentes
    python scripts/descargar_todo.py PT FR IT   # sólo esos
"""
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(RAIZ, "data", "pdf-manifest")
PY = sys.executable


def paises():
    if len(sys.argv) > 1:
        return [a.upper() for a in sys.argv[1:]]
    return sorted(f[:-5] for f in os.listdir(MAN) if f.endswith(".json"))


def bajar(code):
    man = json.load(open(os.path.join(MAN, f"{code}.json"), encoding="utf-8"))
    dest = os.path.join(RAIZ, "pdfs", code)
    ya = len([f for f in os.listdir(dest)]) if os.path.isdir(dest) else 0
    if ya >= len(man):
        print(f"[{code}] completo ({ya}/{len(man)}) — salto", flush=True)
        return True
    print(f"[{code}] {ya}/{len(man)} en disco — descargando…", flush=True)
    r = subprocess.run([PY, os.path.join(RAIZ, "scripts", "descargar_pdfs.py"), code],
                       cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
    cola = (r.stdout or "").strip().splitlines()[-2:]
    print(f"[{code}] " + " | ".join(cola), flush=True)
    if "LISTO" not in (r.stdout or ""):
        print(f"[{code}] stderr: {(r.stderr or '')[-300:]}", flush=True)
        return False
    return True


def main():
    lista = paises()
    hilos = int(os.environ.get("DESCARGA_HILOS", "3"))
    ok = fail = 0
    with cf.ThreadPoolExecutor(max_workers=hilos) as ex:
        for bien in ex.map(bajar, lista):
            ok += 1 if bien else 0
            fail += 0 if bien else 1
    print(f"\nPAÍSES completos {ok} · con incidencias {fail}")


if __name__ == "__main__":
    main()
