#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_entregables.py — Las tres carpetas de entregables (Fase 5).

  entregables/01-md/              los informes en Markdown: la ÚNICA colección
                                  md del repo (la mejorada de Fase 1, con
                                  tablas convertidas; 351 ficheros)
  entregables/02-excel-crudo/     Excel con cita y página (export Fase 2/3)
  entregables/03-excel-normalizado/  generado por 07_normalizar.py: claves
                                  NNNN/AAAA, años de 4 cifras, tipo de suceso
                                  canónico, recomendaciones por celdas

Uso:  python database/scripts/08_entregables.py
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
MD_ORIG = RAIZ / "md" / "ES"                       # md puros (extraídos del PDF)
XLSX_V1 = RAIZ / "database" / "data" / "ciaf_base_global.xlsx"
XLSX_V2 = RAIZ / "entregables" / "03-excel-normalizado" / "ciaf_normalizado.xlsx"
DESTINO = RAIZ / "entregables"


def main() -> int:
    # ---- 01: la única colección md ------------------------------------
    d1 = DESTINO / "01-md"
    d1.mkdir(parents=True, exist_ok=True)
    md = sorted(MD_ORIG.glob("*.md"))
    if not md:
        print("[08] no hay md en md/ES", file=sys.stderr)
        return 1
    # limpia copias anteriores (nunca borra nada fuera de la carpeta)
    for viejo in d1.glob("*.md"):
        viejo.unlink()
    for f in md:
        shutil.copy2(f, d1 / f.name)
    bytes_ = sum(f.stat().st_size for f in md)
    print(f"[08] 01-md/ → {len(md)} md · {bytes_/1e6:.1f} MB")

    # ---- 02: Excel crudo con cita y página ----------------------------
    d2 = DESTINO / "02-excel-crudo"
    d2.mkdir(parents=True, exist_ok=True)
    if not XLSX_V1.exists():
        print(f"[08] falta {XLSX_V1}", file=sys.stderr)
        return 1
    destino = d2 / "ciaf_desde_md_puros.xlsx"
    shutil.copy2(XLSX_V1, destino)
    print(f"[08] 02-excel-crudo/ → {destino.name} "
          f"({destino.stat().st_size/1e6:.1f} MB)")

    # ---- 03: el normalizado ya lo genera 07_normalizar.py ------------
    if XLSX_V2.exists():
        print(f"[08] 03-excel-normalizado/ → {XLSX_V2.name} "
              f"({XLSX_V2.stat().st_size/1e6:.1f} MB)")
    else:
        print("[08] FALTA 03-excel-normalizado → ejecuta 07_normalizar.py")
        return 1

    print("[08] entregables listos en entregables/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
