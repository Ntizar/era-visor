#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracción PDF → Markdown por país.

Uso:
    python extraer_pais.py ES [--force]

Lee pdfs/ES/*.pdf → md/ES/*.md. Detección: si el texto total < 500 chars,
marca el PDF como escaneado (pendiente de OCR) en el propio .md.
"""
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

RAIZ = Path(__file__).resolve().parent.parent
UMBRAL_OCR = 500  # chars mínimos para considerar texto digital


def extraer(codigo: str, force: bool = False):
    src = RAIZ / "pdfs" / codigo
    dst = RAIZ / "md" / codigo
    dst.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(src.glob("*.pdf"))
    print(f"[{codigo}] {len(pdfs)} PDFs a extraer")
    stats = {"ok": 0, "ocr": 0, "skip": 0}
    pendientes = []
    for pdf in pdfs:
        md = dst / (pdf.stem + ".md")
        if md.exists() and not force:
            stats["skip"] += 1
            continue
        try:
            doc = fitz.open(pdf)
            paginas = []
            total_chars = 0
            for i, page in enumerate(doc):
                t = page.get_text()
                total_chars += len(t.strip())
                paginas.append(f"\n\n## Página {i + 1}\n\n{t}")
            n_pag = len(doc)
            doc.close()
            if total_chars < UMBRAL_OCR * max(1, n_pag // 10):
                # escaneado → placeholder pendiente de OCR
                md.write_text(
                    f"---\nescaneado: true\npaginas: {n_pag}\npdf: pdfs/{codigo}/{pdf.name}\n---\n\n"
                    f"[Pendiente de OCR — PDF sin capa de texto]\n",
                    encoding="utf-8",
                )
                stats["ocr"] += 1
                pendientes.append(pdf.name)
                continue
            cuerpo = "".join(paginas)
            front = (
                f"---\npdf: pdfs/{codigo}/{pdf.name}\npaginas: {n_pag}\n"
                f"chars: {total_chars}\n---\n\n"
            )
            md.write_text(front + cuerpo, encoding="utf-8")
            stats["ok"] += 1
        except Exception as e:
            print(f"  ✗ {pdf.name[:60]}: {e}")
    print(f"[{codigo}] RESULTADO: {stats}")
    if pendientes:
        print(f"  Pendientes de OCR ({len(pendientes)}):")
        for p in pendientes[:20]:
            print(f"    - {p}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    codigo = sys.argv[1].upper()
    extraer(codigo, force="--force" in sys.argv)
