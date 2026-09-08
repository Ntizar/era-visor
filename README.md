# ERA Visor — Visor europeo de accidentes ferroviarios

![Fase](https://img.shields.io/badge/Fase-Espa%C3%B1a-blue) ![Informes](https://img.shields.io/badge/Informes-349-green) ![An%C3%A1lisis%20v3](https://img.shields.io/badge/An%C3%A1lisis%20v3-349%2F349-brightgreen) ![Geoloc%20bien](https://img.shields.io/badge/Geoloc%20bien-309-orange)

Visor y base de datos de informes de investigación de accidentes ferroviarios. Convierte los
PDF oficiales (ERA/eRAIL + organismos nacionales como el CIAF) en una **base de datos plana,
filtrable y auditada**, sobre un mapa con la red ferroviaria real de ADIF.

**Ver el visor:** <https://ntizar.github.io/era-visor/>

Hecho con ❤️ por David Antizar

---

## Qué hace (resumen)

1. **Descarga** los informes oficiales por país (scrape de ERA + PDFs originales).
2. **Extrae** el texto (PyMuPDF; OCR solo cuando hace falta) a `.md` legible.
3. **Estructura** cada `.md` a un JSON normalizado con LLM (`qwen3.8-flash`, NaN API).
4. **Enriquece** con taxonomía v2 (subsistema, sistema de protección ASFA/ERTMS/LZB, tipo
   de red, explotación, precursores, mitigaciones, factores humanos, meteorología).
5. **Extrae el análisis v3 completo**: hechos narrativos limpios (sin el índice del PDF),
   cronología minuto a minuto, infraestructura, personal, material rodante, causas
   (directa/contribuyentes/sistémicas), consecuencias, lecciones y recomendaciones.
   **Anti-invención estricta**: si el dato no está en el informe, es `null`.
6. **Geolocaliza** cada informe sobre la vía (métodos en capas, ver abajo).
7. **Audita** todo: distancia real a la vía, cruce PK↔línea, provincia vs red ADIF, y un revisor
   IA que revalida cada JSON contra su informe original.
8. **Visualiza**: mapa con vías ADIF, dashboard con 12+ gráficos, tabla filtrable, ficha de
   detalle completa, export a Excel.

## Estado actual (España)

| Métrica | Valor |
|---|---|
| Informes en la DB | **349** (2006-2025, CIAF + ERA) |
| Con análisis v3 completo | **349/349** |
| Localización auditada | **314 bien · 0 duda · 0 mal · 35 sin coords** |
| Veredicto geo por método | `via_pk` 213 · `via_pkteorico` 78 · `estacion_*`/`poblacion` + · `sin_geo` 41 |
| `VERSION_DATOS` | `2026-09-08-2` (bump en cada despliegue de datos) |

**Residuos conocidos:** 35 sin coords (informes sin PK ni estación en el PDF — no se inventa),
1 pendiente de OCR (`ID_230507_140907`), 1 "mal" que es un patio de clasificación
(`0061/2014`, Tarragona Clasificación — distancia inherente del recinto).

## Estructura del proyecto

```
era-visor/
├── frontend/index.html   ← el visor completo (mapa + dashboard + tabla), IGN WMTS
├── index.html            ← redirect a frontend/index.html (raíz de Pages)
├── scripts/
│   ├── scrape_pais.py             1. descubre informes en ERA
│   ├── descargar_pdfs.py          2. baja PDFs (cortesía 8s, backoff 429)
│   ├── extraer_pais.py            3. PDF → .md (PyMuPDF, OCR solo si hace falta)
│   ├── estructurar_pais.py        4. .md → .json (schema v1, LLM)
│   ├── enriquecer_ia.py           5. .json → campos v2 (taxonomía, LLM)
│   ├── extraer_completo.py        6. análisis v3 (hechos/cronología/causas/lecciones)
│   ├── geocodificar_via.py        7a. PK+línea → punto SOBRE la vía ADIF (interpolación)
│   ├── geocodificar_estacion.py   7b. sin PK → estación IGN (matcher estricto)
│   ├── corregir_ubicaciones.py    8. correcciones verificadas a mano de los "mal ubicados"
│   ├── revisar_localizacion.py    9. AUDITOR: distancia a vía, cruce PK↔línea, provincia
│   ├── revisar_json.py            10. revisor IA: revalida cada JSON contra su .md
│   ├── consolidar.py              11. json/* → data/db/ (dedupe + propaga geo_veredicto)
│   ├── verificar_todo.py          12. comprobación integral PDF↔md↔json↔DB (gate)
│   ├── extraer_erail.py           (helper) Excel eRAIL → JSON por país
│   ├── cruce_erail.py             (helper) cruza eRAIL ↔ PDFs descargados
│   └── importar_ciaf.py           (helper) importa los informes CIAF verificados
├── data/
│   ├── pdf-manifest/  ← qué PDFs hay por país (ES.json)
│   ├── erail/         ← Excel eRAIL convertido a JSON
│   ├── cruce/         ← cruce eRAIL ↔ PDF
│   ├── adif-tramos.geojson + adif-pkteoricos.geojson  ← red ADIF (WFS IDEADIF)
│   ├── ign-estaciones{1,2}.json  ← estaciones IGN (~2.000, FeatureServer)
│   ├── revision/      ← auditoría: ES-localizacion.json, ES-verificacion.md
│   └── db/            ← SALIDA FINAL: index.json + reports/ES.json + recs/
├── json/ES/           ← un JSON por informe (+ /v3/ con el análisis completo)
├── md/ES/             ← un .md por informe (texto extraído del PDF)
├── pdfs/              ← PDFs originales (fuera de git, ver .gitignore)
└── docs/              ← estructura del informe, taxonomías, análisis inicial
```

### Nota sobre `_duplicados_descartados/`
En `json/ES/_duplicados_descartados/`, `json/ES/v3/_duplicados_descartados/` y
`md/ES/_duplicados_descartados/` se archivan los JSON/MD **duplicados descartados por el
dedupe** (CIAF viejos sin análisis, duplicados por contenido). **Nunca se borran** — quedan
como evidencia de que no se perdió ningún dato. `verificar_todo.py --limpiar` archiva ahí los
duplicados por md5.

## Geolocalización (la clave de la calidad)

La ubicación es lo que más errores ha dado. Se resuelve por capas, de más a menos preciso; el
`metodo_geo` de cada registro indica cuál se usó:

| `metodo_geo` | Cuándo | Fiabilidad |
|---|---|---|
| `via_pk` | PK + línea con código → interpolar en el tramo ADIF de ESA línea | Máxima (punto SOBRE la vía) |
| `via_pkteorico` | PK sin línea casable → PKTeórico más cercano de la línea+provincia | Alta |
| `estacion_ign` | Sin PK → estación IGN (matcher estricto por palabra completa) | Media-alta |
| `estacion_adif` | Estación de la red ADIF (OSM/OpenData) | Media |
| `poblacion` | Línea sin geometría en ADIF / estación sin mapear → centro urbano declarado | Media (regla de David) |
| `previa` | Sin match → conserva la coordenada previa (NPI) | Baja → señal de revisión |

### Bugs de geolocalización corregidos (lecciones duras)

- **`codtramo` estructura**: es `eje(2)+línea(3)+seq(4)` (9 dígitos). El código de línea vive en
  `codtramo[2:5]`, **nunca** en `codtramo[:3]` (cruzaba líneas — Caleyo aterrizaba en Guadalajara).
- **Línea sin código numérico** (`Valencia - San Vicente de Calders`): `parse_linea` devolvía
  `None` → el geocodificador no casaba por línea y caía al fallback por provincia, cruzando a
  OTRA línea (34/2007 → pk 244,350 en la línea 200 de Zaragoza). **Fix**: si la línea no trae
  código, recuperarlo del texto del informe (`ubicacion_nombre`: "(600 Valencia-San Vicente...
  railway line)") → interpolación en la línea correcta.
- **`id_provinc=0` en PKTeóricos**: los PK de líneas correctas a menudo vienen con provincia
  "desconocida" (0). El filtro `if idps and to_int(idp) not in idps: continue` los descartaba
  TODOS → match vacío → se conservaba la coord previa stale. **Fix**: solo excluir provincias
  CONOCIDAS distintas (`idp not in (None,0) and idp not in idps`).
- **Matcher de estación por substring es peligroso**: "Parc" casó "Elx-Parc" con Sabadell Parc
  del Nord (Barcelona). Matcher estricto por palabra completa o abstención.
- **`poblacion` no es un error**: cuando la línea no tiene geometría en ADIF (línea 510
  Aljucén-Cáceres) o la estación no está mapeada, el punto se pone en el centro urbano
  declarado (regla de David). El auditor lo marca "bien" — es el método elegido, no un fallo.

## Cómo procesar un país nuevo (ej. Alemania)

```shell
python scripts/scrape_pais.py DE          # 1. descubre informes en ERA
python scripts/descargar_pdfs.py DE       # 2. baja PDFs (lento: cortesía 8s)
python scripts/extraer_pais.py DE         # 3. PDF → MD
python scripts/estructurar_pais.py DE     # 4. MD → JSON (LLM)
python scripts/enriquecer_ia.py DE        # 5. campos v2 (LLM)
python scripts/extraer_completo.py DE     # 6. análisis v3 (LLM)
python scripts/geocodificar_via.py DE     # 7a. coords sobre la vía (← red del país)
python scripts/geocodificar_estacion.py DE# 7b. o por estación (← dataset del país)
python scripts/corregir_ubicaciones.py DE # 8. correcciones verificadas a mano
python scripts/revisar_localizacion.py DE # 9. auditoría (veredictos)
python scripts/revisar_json.py DE         # 10. revisor IA
python scripts/consolidar.py DE           # 11. → data/db/ (dedupe + geo_veredicto)
python scripts/revisar_localizacion.py DE # 12. RE-auditar la DB (el auditor lee coords de la DB)
python scripts/verificar_todo.py DE       # 13. comprobación integral (gate; --limpiar duplicados)
```

**Orden crítico (ida y vuelta):** geocodificar → consolidar → **auditar** → consolidar →
verificar_todo. El auditor lee las coords de la DB; tras consolidar hay que re-auditar y
re-consolidar hasta que las cifras cuadren. Todo es **reanudable** (relanza el mismo comando).

### Nota para países que no son España
- La red ferrovia para geolocalizar debe descargarse para cada país (ADIF geojson es solo ES).
  ERA/eRAIL no da coordenadas; hay que interpolar sobre la red nacional.
- Los informes llegan en el idioma del país. El pipeline extrae `titulo_normalizado` en
  **castellano** + `idioma_original` (los títulos sin traducir se rechazan). Este es el
  trabajo pendiente para las fases 2+.

## El schema del JSON

Cada informe (`json/<PAIS>/<id>.json`, análisis completo en `json/<PAIS>/v3/<id>.json`):

| Campo | Qué es |
|---|---|
| `id`, `titulo`, `fecha`, `hora` | identificación (+ `titulo_normalizado`, `idioma_original`) |
| `expediente` | referencia oficial (`0034/2007`) |
| `provincia`, `estacion`, `pk`, `linea` | localización textual |
| `lat`, `lng`, `metodo_geo` | coordenadas + método (`via_pk`, `poblacion`, `estacion_ign`…) |
| `fallecidos`, `heridos_graves`, `heridos_leves`, `danos_materiales`, `gravedad` | consecuencias (v3 MANDÁ sobre el base) |
| `subsistema`, `sistema_proteccion`, `tipo_red`, `explotacion` | taxonomía v2 |
| `precursores`, `mitigaciones`, `factores_humanos`, `meteorologia` | causas y contexto v2 |
| `v3.hechos` | narrativa limpia (2-4 párrafos, sin el índice del PDF) |
| `v3.cronologia` | eventos minuto a minuto |
| `v3.infraestructura` | señalización, tipo de vía, velocidad máx, ancho, electrificación |
| `v3.personal`, `v3.trenes`, `v3.material_rodante` | implicados |
| `v3.causas` | directa, contribuyentes, sistémicas |
| `v3.lecciones`, `v3.recomendaciones` | con destinatario |
| `url_pdf`, `archivo_pdf` | enlace al PDF original (los PDFs nunca van en la DB) |
| `geo_veredicto`, `geo_dist_m`, `geo_motivo` | del auditor (propagado a la DB por `consolidar.py`) |

## Despliegue

GitHub Pages vía workflow moderno (`.github/workflows/pages.yml`, `actions/deploy-pages@v4`),
deploy directo desde `main`. La DB es JSON estático servido tal cual por Pages.

**Cache-busting obligatorio:** `VERSION_DATOS` (const en `frontend/index.html`) se bumpa en cada
despliegue de datos y se añade `?v=` a cada fetch de la DB. Sin esto el navegador cachea el JSON
de MBs y "sigue saliendo mal" aunque el servidor ya esté bien.

## Hoja de ruta

- **Fase 1 (actual): España al 100%.** Queda: OCR del informe pendiente, decisión sobre los
  4 dudosos, y validar los 35 sin coords contra la fuente.
- **Fase 2: Alemania** (452 PDFs detectados), Francia, Italia, Polonia.
- **Traducción** de los informes al castellano en el pipeline (`titulo_normalizado` +
  `idioma_original`), no solo campos cortos.
- **Capas extra:** meteorología del día del accidente (Open-Meteo histórico), LTV.
- **API JSON pública** (Pages ya sirve `data/db/`).

## Referencias

- `docs/analisis-inicial.md` — análisis de exploración de la fuente (eRAIL, web ERA, conteos por
  país) — úsalo como punto de partida para otros países.
- `docs/taxonomias-kaizen.md` — estructura mínima del informe según RD 929/2020, RD 623/2014 y
  Reglamento (UE) 2020/572.
- `docs/estructura-informe-kaizen.docx` — estructura del informe (KAIZEN).

## Licencia

Datos: fuentes oficiales (ERA/eRAIL, CIAF, ADIF, IGN — CC BY 4.0). Código: libre.
Hecho con ❤️ por David Antizar