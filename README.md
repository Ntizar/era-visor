# ERA Visor — Accidentes ferroviarios en Europa

Visor y base de datos estructurada de los informes de investigación de accidentes ferroviarios europeos (ERA / eRAIL + organismos nacionales de investigación).

**Estado:** fase inicial (scraping España).

## Objetivo

Disponer una BBDD plana que permita filtrar por conceptos asociados a los accidentes y obtener frecuencias, severidades y mitigaciones — para estimaciones de riesgo, evaluación de medidas de explotación (ASFA, tipo de vía, bloqueo, ATP…) e identificación de precursores.

- **Fase 1:** extracción completa de los informes (estructura del Reglamento UE 2020/572) + export Excel
- **Fase 2:** categorización IA (tipo de vía, bloqueo, ATP, clima, precursores, mitigaciones) sobre BBDD estática

## Arquitectura

```
web ERA (Drupal, país/año) ─► scripts/scrape_pais.py ─► data/pdf-manifest/*.json
                           └► scripts/descargar_pdfs.py ─► pdfs/ES/*.pdf (no al repo)
PDF ─► PyMuPDF/OCR ─► md/ES/*.md ─► LLM + cruce eRAIL ─► json/ES/*.json
                                  └► scripts/consolidar.py ─► data/db/ (index + por año)
data/db ─► frontend (Leaflet + Chart.js, GitHub Pages, export Excel)
```

- **DB plana JSON sin imágenes** — el PDF original siempre queda enlazado (trazabilidad)
- Textos largos en `.md` por informe (base para RAG / modelos)
- Todo en castellano; contenido multi-idioma: campos cortos traducidos, original siempre accesible

## Scripts

| Script | Uso |
|---|---|
| `scripts/scrape_pais.py ES` | Manifest de PDFs por país |
| `scripts/descargar_pdfs.py ES` | Descarga reanudable de PDFs (1 req/s) |

## Fuentes

- [ERA — Accident Investigation Reports](https://www.era.europa.eu/era-folder/accident-investigation-reports) (30 países)
- [Excel eRAIL 07.08.2026](https://www.era.europa.eu/sites/default/files/2026-08/erail%20database%2007.08.2026.xlsx) (4.067 investigaciones, 8.588 recomendaciones)

Hecho con ❤️ por David Antizar
