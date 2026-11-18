# -*- coding: utf-8 -*-
"""descargar_todo.py — descarga los PDFs de todos los países con manifiesto, en serie.

Reanudable: salta lo ya descargado. Pausa entre países para no despertar el 429 de ERA.

Uso:
    python scripts/descargar_todo.py            # todos los manifiestos presentes
    python scripts/descargar_todo.py PT FR IT   # sólo esos
"""
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


def main():
    total_ok = total_fail = 0
    for code in paises():
        man = json.load(open(os.path.join(MAN, f"{code}.json"), encoding="utf-8"))
        dest = os.path.join(RAIZ, "pdfs", code)
        ya = len([f for f in os.listdir(dest)]) if os.path.isdir(dest) else 0
        if ya >= len(man):
            print(f"[{code}] completo ({ya}/{len(man)}) — salto")
            continue
        print(f"[{code}] {ya}/{len(man)} en disco — descargando…", flush=True)
        r = subprocess.run([PY, os.path.join(RAIZ, "scripts", "descargar_pdfs.py"), code],
                           cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
        cola = (r.stdout or "").strip().splitlines()[-3:]
        print("   " + " | ".join(cola), flush=True)
        if "LISTO" in (r.stdout or ""):
            total_ok += 1
        else:
            total_fail += 1
            print("   stderr:", (r.stderr or "")[-300:])
        time.sleep(5)
    print(f"\nPAÍSES completos {total_ok} · con incidencias {total_fail}")


if __name__ == "__main__":
    main()
