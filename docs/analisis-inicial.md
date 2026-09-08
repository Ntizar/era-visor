# Análisis — Visor Europeo de Accidentes Ferroviarios (ERA/eRAIL)

Fecha: 2026-08-28 · Sesión de exploración inicial · Mastermind para David Antizar

---

## 1. Qué existe en la fuente

### 1.1 Excel eRAIL (descargado: `data/erail.xlsx`, 5,3 MB)
- **Hoja "Investigations": 4.067 investigaciones × 64 columnas** (4.048 con país válido)
- **Hoja "Safety recommendations": 8.588 recomendaciones × 9 columnas**
- 1.748 fallecidos acumulados; 3.253 registros con causa directa descrita

**Distribución por país (top):**
| País | Investigaciones |
|---|---|
| Chequia | 589 |
| Rumanía | 538 |
| Hungría | 499 |
| Reino Unido | 370 |
| **España** | **357** |
| Alemania | 262 |
| Noruega | 160 |
| Austria | 158 |
| Dinamarca | 123 |
| Francia | 106 |
| Finlandia | 102 |
| Italia | 98 |
| ... (30 países + Túnel del Canal) | |

**Columnas clave ya normalizadas por ERA:** tipo de informe, estado, título, cuerpo investigador, fecha/hora, tipo de suceso + descripción, país, nombre de ubicación, tipo de línea/ubicación/movimiento, RU e IM implicados, **víctimas por categoría** (pasajeros, personal, usuarios de paso a nivel, personas no autorizadas, otros — mortales y heridos graves separados), costes materiales estimados, base legal, decisión de investigar, nº de recomendaciones asociadas, **causa directa y causas sistémicas en texto**, fechas de todo el ciclo (notificación, informe provisional, final, cierre).

⚠️ La columna "Investigation report" está casi vacía (4.033/4.067): **los enlaces a PDFs NO están en el Excel**.

### 1.2 Web de informes (era.europa.eu/era-folder/accident-investigation-reports)
- Índice con **30 países** (27 UE + CH, NO, Serbia, UK)
- Cada país es un "book" de Drupal con **una página por año** (España: 2006–2025)
- Cada página de año es **HTML estático con enlaces directos a PDFs** en `/system/files/...`
- España: ~357 investigaciones → **680 PDFs únicos** (hay informes finales + notas de avance + anexos por suceso)
- Alemania: 452 PDFs
- El `rel=next` salta entre países → scrapeando por enlaces de año de cada país, NO siguiendo next

### 1.3 PDFs — calidad de texto (muestreo 6 aleatorios ES)
| PDF | Tamaño | Páginas | Texto | Imgs |
|---|---|---|---|---|
| FI 2008 DataSummary | 41 KB | 1 | **0 (escaneado)** | 1 |
| C2 2005 Report | 1,1 MB | 55 | 79.380 | 35 |
| ID-271206 | 103 KB | 7 | 13.072 | 0 |
| RS nota avance | 148 KB | 2 | 1.606 | 0 |
| B3 Summary | 63 KB | 1 | 1.733 | 0 |
| B5 2007 report | 1,6 MB | 52 | 85.645 | 75 |

**Conclusión:** mayoría con texto seleccionable → PyMuPDF directo; minoría escaneada → OCR (ocrmypdf/Tesseract). Un pequeño paso previo de detección (texto<500 chars ⇒ OCR) resuelve la bifurcación.

### 1.4 CIAF-visor (referencia España)
- Repo `Ntizar/CIAF-visor`: 270 informes ES parseados, geolocalizados, con esquema rico
- `data/index.json` (metadatos) + `data/reports/YYYY.json` (particionado por año, patrón ya validado)
- Campos: expediente, título, tipo, gravedad, fecha, ubicación (estación/provincia/lat/lng), entidades, víctimas, resumen, análisis, conclusiones, recomendaciones
- Lecciones acumuladas en el skill `government-data-pipelines`: extracción por páginas (no regex global), LLM para causas (100% vs 72% regex), geocoding por prioridad (DB local > PK/LTV > Nominatim), nunca borrar, todo castellano

---

## 2. Arquitectura propuesta

### 2.1 Pipeline de datos (por país, incremental)

```
Fase A — Scraping          scripts/scrapeera/scrape_pais.py <ES|DE|...>
  Web ERA (páginas año) ──► data/pdf-manifest/ES.json (enlaces + año + país)
                        └─► pdfs/ES/*.pdf (descarga con UA, reanudable)

Fase B — Extracción        scripts/scrapeera/extraer_pais.py <ES>
  PDF ──► PyMuPDF texto ──► md/ES/ID.md  (texto largo, castellano u original)
       └► (si escaneado) ─► OCR ocrmypdf ─► md
  OCR selectivo solo donde texto<500 chars (≈10-20% según país/época)

Fase C — Estructuración    scripts/scrapeera/estructurar_pais.py <ES>
  Cruce eRAIL (Excel) + texto .md ──► LLM (qwen NaN) con schema pydantic
  ──► json/ES/ID.json (schema unificado abajo)

Fase D — Consolidación     scripts/scrapeera/consolidar.py
  json/*/*.json ──► data/db/
     ├── index.json          (~2-5 MB, metadatos mínimos para mapa)
     ├── reports/YYYY.json   (particionado por año, payload completo)
     ├── recs.json           (8.588 recomendaciones, vinculación por ERAIL ID)
     └── coords.json         (cache de geocoding)

Fase E — Visor (frontend estático, GitHub Pages)
  index.html + Leaflet + Chart.js, carga index.json on demand
```

**Por qué esta forma:** mismo patrón validado en CIAF-visor; GitHub Pages sirve JSON estático sin backend; particionado por año mantiene el front por debajo de los límites cómodos; los .md preservan el texto largo para RAG/modelos futuros sin hinchar la DB del visor.

### 2.2 Base de datos plana (sin imágenes — lo que pide David)

Principio: **una tabla de eventos plana + tablas satélite, en JSON; PDFs nunca dentro, solo enlace**.

```
schema del evento (plano, castellano):
  id                  "ES-2006-0054"  (pais-año-correlativo)
  pais, ano
  expediente          "0054/2006"
  titulo
  tipo_informe        final|interino|resumen
  fecha_suceso, hora
  tipo_suceso         descarrilamiento|colision|arrollamiento|... (taxonomía ERA)
  suceso_descripcion
  linea_tipo, ubicacion_tipo, movimiento_tipo, sistema_ferroviario
  ubicacion_nombre, provincia, lat, lng
  ru_implicadas[], im_implicadas[]
  fallecidos {pasajeros, personal, paso_nivel, no_autorizados, otros, total}
  heridos_graves {...ídem}
  costes_eur
  causa_directa       (texto)
  causas_sistemicas   (texto)
  recomendaciones[{id, texto, destinatario}]
  fuente {url_pdf, url_pagina, cuerpo_investigador}
  idioma_original
  traducciones {titulo_es, resumen_es}  ← solo campos cortos
```

**Tamaño estimado:** texto de causas/resúmenes ≈ 1-3 KB/registro × 4.000 = **6-12 MB total en JSON planos** — perfecto para Pages. Los .md completos (texto largo) viven aparte en el repo, NO en la DB del visor. Nada de imágenes en la DB: si algún día se quieren, se extraen a `img/` y se enlaza.

### 2.3 Visor
- **Mapa Leaflet** fondo abierto (OSM) + capa de **red ferroviaria europea**
  - España: WMS Tramificación ADIF (ya validado) — resto de Europa: Overpass pre-descargado y simplificado (regla: <10 MB, coords 4 decimales, sampler cada 3)
- **Dashboards** Chart.js: evolución temporal (regresión sobre 20 años, no medias simples), por tipo de suceso, por país, víctimas por categoría, causas más frecuentes
- **Filtros cruzados**: país, año, tipo, víctimas, RU/IM, con/graves, tipo de línea
- **Detalle del suceso**: resumen en castellano, causas, recomendaciones, enlace al PDF original SIEMPRE (trazabilidad)
- **Export Excel**: botón por vista/filtro → genera XLSX con SheetJS de lo filtrado
- **Capas extra (futuro)**: clima del día (Open-Meteo Archive API, por coords+fecha, cacheable), densidad de tráfico, ECDC, etc.
- **Multi-idioma**: i18n ES/EN en la interfaz; contenido traducido solo en campos cortos (título/resumen); texto completo queda en idioma original con vista .md

### 2.4 i18n de contenido (original ↔ castellano)
- Campos estructurados: traducción batch de `titulo` y `resumen` con qwen (NaN) → `traducciones.es`
- Texto largo: el .md original siempre accesible; traducción a demanda (coste) o por lotes nocturno para los resúmenes
- Taxonomía de tipos de suceso: diccionario ERA → castellano (tabla fija, sin traducción runtime)

### 2.5 Para modelos/IA (segunda vida de los datos)
- Los .md por informe + schema JSON plano son la base perfecta para RAG (ChromaDB, ya operativa en Mastermind)
- Posibles estudios: causalidad por tipo de línea, NLP clustering de causas sistémicas, comparativa pre/post Directiva 2004/49
- El Excel eRAIL original se mantiene como "fuente cruda" y el JSON plano como "fuente curada"; nunca se mezclan

---

## 3. Plan de ejecución

### Fase 0 — España (ya decidido con David)
1. Scrape de la web ES por años correctos (lista real de ~357 investigaciones / ~680 PDFs)
2. Descarga a `pdfs/ES/` (reanudable, 1 req/s, ~680 archivos ≈ 30-60 min)
3. Detección texto/OCR → `md/ES/`
4. **Reutilizar los 270 JSONs de CIAF-visor** como semilla del schema; parsear los que falten (informes 2006-2008 ID-*, notas de avance, y PDFs que CIAF-visor no cubría)
5. Cruce con eRAIL (357 filas ES) para completar víctimas por categoría, tipo de movimiento, RU/IM, causas
6. Consolidar → visor

### Fase 1 — Visor ES completo
Mapa + dashboard + filtros + export Excel + detalle con PDF original.

### Fase 2 — País a país (orden por volumen/valor)
DE (262/452 PDFs) → FR → IT → PL → … replicando el pipeline. El scraper ya es genérico: solo cambia el slug del país (`/era-folder/de-investigations`, etc.) y el idioma de los PDFs (DE/FR/IT → necesitarán traducción de título+resumen).

### Fase 3 — Mejoras
Capa clima (Open-Meteo), isócronas de puntos negros, recomendaciones vinculadas entre países, API de consulta, embeddings.

---

## 4. Riesgos y decisiones abiertas

| Riesgo | Mitigación |
|---|---|
| PDFs escaneados en otros idiomas (DE/FR antiguos) | OCR + presupuesto de tokens; empezar por texto seleccionable |
| Excel con datos incoherentes (visto: provincias erróneas en CIAF) | El texto del informe manda sobre el Excel; cruce por expediente normalizado |
| Volumen LLM (4.000 informes × extracción) | qwen3.8-flash es barato; batch nocturno por país; cache por ID |
| Geocoding masivo | Prioridad: eRAIL location name + coords de CIAF-visor > DB local > Nominatim con cache |
| Legal | Todo es información pública de ERA (informes de investigación); atribución a ERA/cuerpos nacionales; sin imágenes |

**Decisiones pendientes de David:**
1. ¿Visor como proyecto GitHub Pages nuevo (p.ej. `Ntizar/era-visor`) o dentro de un repo existente?
2. ¿Dónde vive el repo de datos? (propuesto: `~/Projects/era-accidentes` → repo GitHub con `data/` y `pdfs/` en .gitignore o LFS, los .md sí al repo)
3. ¿Empiezo ya con la Fase 0 (descarga 680 PDFs ES + consolidación con CIAF-visor)?

---

*Hecho con ❤️ por David Antizar — Mastermind es ejecutor, David es autor.*
