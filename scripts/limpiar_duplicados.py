# -*- coding: utf-8 -*-
"""limpiar_duplicados.py — aparta los md-es que no corresponden a ningún md (o duplican).

Durante las primeras tandas se generaron ficheros con nombres distintos para el mismo
informe (entidades HTML, años mal deducidos, tildes). Eso infla las cuentas (4.310 ficheros
para 3.963 informes) y puede liar al que consulte la carpeta.

Aquí se detecta:
  · huérfanos: su `md_origen` no existe
  · duplicados: dos md-es apuntan al mismo md (se queda el más reciente)

No borra: MUEVE a `data_antigua/md-es-sobrantes/<CC>/` para poder recuperarlos.

Uso:
    python scripts/limpiar_duplicados.py            # informe, no toca nada
    python scripts/limpiar_duplicados.py --aplicar  # los mueve
"""
import argparse
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_ES = os.path.join(RAIZ, "md-es")
DESTINO = os.path.join(RAIZ, "data_antigua", "md-es-sobrantes")
IGN = ("indice", "índice", "leeme", "readme")


def cabecera(p):
    t = open(p, encoding="utf-8", errors="replace").read(1200)
    m = re.match(r"^---\r?\n(.*?)\r?\n---", t, re.S)
    d = {}
    if m:
        for l in m.group(1).splitlines():
            if ":" in l:
                k, v = l.split(":", 1)
                d[k.strip()] = v.strip().strip('"')
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()

    por_origen = {}
    huerfanos = []
    total = 0
    for dp, _, fs in os.walk(MD_ES):
        for f in fs:
            if not f.endswith(".md") or f.lower().startswith(IGN):
                continue
            p = os.path.join(dp, f)
            total += 1
            origen = cabecera(p).get("md_origen", "")
            ruta_or = os.path.join(RAIZ, origen.replace("/", os.sep)) if origen else ""
            if not origen or not os.path.exists(ruta_or):
                huerfanos.append(p)
                continue
            por_origen.setdefault(origen, []).append(p)

    duplicados = []
    for origen, lista in por_origen.items():
        if len(lista) > 1:
            lista.sort(key=os.path.getmtime, reverse=True)
            duplicados += lista[1:]          # se queda el más reciente

    sobran = huerfanos + duplicados
    print(f"md-es totales: {total}")
    print(f"  huérfanos (su md no existe): {len(huerfanos)}")
    print(f"  duplicados (mismo md, otro nombre): {len(duplicados)}")
    print(f"  a apartar: {len(sobran)}  →  quedarían {total - len(sobran)}")

    if not a.aplicar:
        for p in sobran[:10]:
            print("   " + os.path.relpath(p, RAIZ))
        return

    for p in sobran:
        code = os.path.relpath(p, MD_ES).split(os.sep)[0]
        rel = os.path.relpath(p, MD_ES)
        dst = os.path.join(DESTINO, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(p, dst)
    print(f"movidos {len(sobran)} ficheros a {os.path.relpath(DESTINO, RAIZ)}")


if __name__ == "__main__":
    main()
