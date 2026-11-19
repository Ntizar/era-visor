# Auditoría del OCR

Generado por `scripts/ocr_escaneados.py` el 2026-11-19. Un registro por informe en `data/ocr/<CC>.json`.

Motor: **Tesseract** con `tessdata_best` a 300 dpi. La confianza es la media por palabra que declara el propio Tesseract (0-100); por debajo de 70 el texto se considera dudoso y se revisa a mano antes de traducir.

| País | Informes OCR | Páginas | Páginas vacías | Confianza media | Motor |
|---|---|---|---|---|---|
| BE | 1 | 18 | 0 | 82.3 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| BG | 4 | 60 | 0 | 68.2 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| FI | 63 | 67 | 1 | 93.5 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| FR | 3 | 23 | 0 | 90.1 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| HR | 4 | 73 | 0 | 93.5 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| IT | 19 | 632 | 12 | 89.1 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| LT | 2 | 3 | 0 | 94.7 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| NO | 1 | 1 | 0 | 70.0 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| PL | 28 | 506 | 5 | 85.3 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| PT | 3 | 38 | 0 | 92.2 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| SE | 1 | 55 | 0 | 91.8 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| SI | 28 | 1302 | 4 | 92.6 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |
| SK | 2 | 33 | 1 | 87.9 | tesseract v5.4.0.20240606 (tessdata_best, 300 dpi) |

**Total OCR-eados: 159**
