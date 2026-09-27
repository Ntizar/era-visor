#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR del PDF escaneado ID_230507_140907 → md/ES/ (Tesseract 5.4, spa, 300 dpi).

Único informe de los 372 sin capa de texto (Corel PHOTO-PAINT, imágenes puras).
Escribe el .md con el mismo frontmatter y el mismo marcado `## Página N` que
el resto de md/ES/ para que el pipeline (json → v3 → DB) lo procese igual.

Uso:  python ocr_pendiente.py
"""
import fitz
import hashlib
import os
import time

PDF = os.path.join(os.path.dirname(__file__), "..", "pdfs", "ES", "ID_230507_140907.pdf")
OUT = os.path.join(os.path.dirname(__file__), "..", "md", "ES", "ID_230507_140907.md")
TESSDATA = os.path.join(os.environ["LOCALAPPDATA"], "tesseract", "tessdata")
DPI = 300
IDIOMA = "spa"


def main():
    PDF_ABS = os.path.abspath(PDF)
    OUT_ABS = os.path.abspath(OUT)
    with open(PDF_ABS, "rb") as fh:
        md5 = hashlib.md5(fh.read()).hexdigest()
    doc = fitz.open(PDF_ABS)
    t0 = time.time()
    paginas = []
    for i in range(doc.page_count):
        pg = doc[i]                      # referencia viva: get_text exige page.parent
        tp = pg.get_textpage_ocr(dpi=DPI, full=True, tessdata=TESSDATA, language=IDIOMA)
        txt = pg.get_text(textpage=tp).strip()
        paginas.append(txt)
        print(f"  pagina {i+1}/{doc.page_count}: chars={len(txt)}", flush=True)
    cuerpo = "\n\n".join("## Página %d\n\n%s" % (i + 1, t) for i, t in enumerate(paginas))
    total = sum(len(t) for t in paginas)
    front = (
        "---\n"
        "pdf: pdfs/ES/ID_230507_140907.pdf\n"
        "md5_pdf: %s\n"
        "paginas: %d\n"
        "chars: %d\n"
        "escaneado: false\n"
        "ocr: tesseract 5.4 spa dpi300\n"
        "fecha_proceso: 2026-09-27\n"
        "---\n\n%s\n" % (md5, doc.page_count, total, cuerpo)
    )
    with open(OUT_ABS, "w", encoding="utf-8") as fh:
        fh.write(front)
    print("TOTAL chars %d · %.1fs -> %s" % (total, time.time() - t0, OUT_ABS))
    print("--- muestra pagina 1 ---")
    print(paginas[0][:700])


if __name__ == "__main__":
    main()
