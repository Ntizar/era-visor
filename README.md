# ERA Visor — Visor europeo de accidentes ferroviarios

![Fase](https://img.shields.io/badge/Fase-Espa%C3%B1a-blue) ![Informes](https://img.shields.io/badge/Informes-351-green) ![An%C3%A1lisis%20v3](https://img.shields.io/badge/An%C3%A1lisis%20v3-351%2F351-brightgreen) ![Geoloc%20bien](https://img.shields.io/badge/Geoloc%20bien-344-green) ![%C3%8Dndice%20CIAF](https://img.shields.io/badge/%C3%8Dndice%20CIAF-281%2F351-informational)

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
| Informes en la DB | **351** (2006-2025, CIAF + ERA) |
| En el índice oficial del CIAF | **281** · los otros 70 (2006-2007) solo vía ERA — ver «De dónde sale cada dato» |
| Con análisis v3 completo | **351/351** |
| Localización auditada | **344 bien · 0 duda · 4 mal · 3 sin coords** (99 % con punto) |
| Veredicto geo por método | `via_pk` 209 · `via_pkteorico` 82 · `estacion_ign` 39 · `poblacion` 17 · `estacion_adif` 1 · `sin_geo` 3 |
| Recomendaciones estructuradas | **651 en la DB · 644 en el Excel normalizado** (destinatario/implementador/texto/página en celdas separadas) |
| `VERSION_DATOS` | `2026-09-28-1` (bump en cada despliegue de datos) |

## De dónde sale cada dato (procedencia)

Regla de oro: **cada dato lleva su fuente al lado** (cita literal + página en el crudo,
`metodo_geo` en la localización, `procedencia` en los derivados). Resumen:

| Dato | Fuente | Dónde vive |
|---|---|---|
| Informes (PDF) | Scrape de ERA/eRAIL + índice del CIAF | `pdfs/ES/` (fuera de git) · `data/pdf-manifest/ES.json` |
| Markdown | PDF → texto (PyMuPDF, OCR si hace falta), **mejorado en Fase 1** (tablas → markdown) | `md/ES/` — **la única colección md**; originales en `data_antigua/md_originales/` |
| Campos de la guía CIAF (0.x-7.x) | Fase 2, extracción **determinista** del md con cita + página | `database/data/crudo/` (351 JSON, uno por expediente) |
| Huecos que el informe no rellena | Fase 4B, LLM que SOLO rellena huecos con cita verificada; nunca pisa un valor determinista | `database/data/mejorado/` → hoja `Mejorado` del Excel |
| Taxonomía v2 y análisis v3 | LLM con anti-invención estricta: si el informe no lo dice, `null` | `json/ES/*.json` + `json/ES/v3/` (351) |
| Coordenadas | Geocodificación por capas sobre la red ADIF (ver «Geolocalización») + auditor | `data/db/` (`metodo_geo`, `geo_veredicto`) |
| Clima del día | Reanálisis ERA5 vía Open-Meteo Archive (gratis, ~25 km) | `data/db/clima.json` |
| `indice_oficial` | Cruce con el índice de la web del CIAF (scrape 2026-09-26: `database/data/listado_web_ciaf.json`) | `data/db/` y columna `en_indice_oficial_ciaf` del Excel |

### Los 281 del índice oficial vs los 70 que no aparecen

El índice online del CIAF (transportes.gob.es, 2007-2025) lista **281 informes**, verificado
año a año; el cruce por expediente casa **281/281**. Los otros **70** (34 de 2006 y 36 de
2007) son informes finales reales que el CIAF **no publica hoy en su índice** (el índice
empieza en 2007 con solo 4): se conocen por el espejo de ERA/eRAIL y por los PDF originales.
Mismo tratamiento y misma auditoría que el resto. En el visor hay un filtro «Índice oficial
CIAF» para separarlos y el listado completo está en
[`data/revision/281-vs-70.md`](data/revision/281-vs-70.md).

### Los 21 duplicados del Excel del CIAF

El Excel de partida traía 21 expedientes con DOS documentos (IF + nota de 2-3 páginas,
final + interim, español + inglés de eRAIL). Regla aplicada: **se queda el de más páginas
e información** (desempate por nº de campos, luego alfabético). El ganador es la fila del
Excel; el descartado **no se borra**: vive en `database/data/duplicados_excel/` con su traza
en `database/data/dedupe_map.json` y las columnas `n_documentos`, `tipo_documento2` y
`descartado_pdf`. Las 21 decisiones, una a una:
[`data/revision/dedupe-excel.md`](data/revision/dedupe-excel.md).

### Lo que NO aparece (y por qué)

- **3 sin coordenadas**: Barcelona Marina (estación de Cercanías abierta en 2022, ausente de
  IGN/OSM), Río Huerva (apeadero sin mapear), puesto de bloqueo Río Duero (nombre no
  localizable) y el escaneado `0033/2007`, cuya fuente pública no da estación. **No se inventa.**
- **3 sin clima**: los mismos sin coordenadas.
- **Campo 3.7.3 de la guía** («Información sobre riesgos, defectos…»): vacío en el 100 % de
  los informes — la guía lo contempla pero el CIAF no lo rellena nunca (igual que «0.5
  Fecha del informe», documentada como «no publica»).
- **Versiones antiguas** (md originales, JSON de los duplicados, entregables viejos):
  archivadas en `data_antigua/` — nada borrado.
- **17 ficheros md con nombres corruptos** (`201vila.md"`, `241 de Henares.md"`…): residuo de
  un bug antiguo de extracción; ya no estaban en disco, git los purga en el próximo commit.

## Entregables

Se generan con `database/scripts/08_entregables.py`, que parte de la normalización de
`database/scripts/07_normalizar.py` (contrato en `database/SPEC-NORMALIZACION.md`):

| Ruta | Qué es |
|---|---|
| `entregables/01-md/` | Los **351** informes en Markdown — la colección única (mejorada, con tablas convertidas) |
| `entregables/02-excel-crudo/` | `ciaf_desde_md_puros.xlsx` — Excel con cita y página de cada dato (export Fase 2/3), columna `en_indice_oficial_ciaf` |
| `entregables/03-excel-normalizado/` | `ciaf_normalizado.xlsx` — claves `NNNN/AAAA`, años a 4 cifras, taxonomía única de `tipo_suceso`, `categoria_suceso`, recomendaciones en celdas separadas y expediente normalizado |
| `entregables/base_ciaf.json` | Base única: 351 informes + 644 recomendaciones |

**Verificación de la normalización (salida real):** 41.319 claves/expedientes comprobados ·
**0** mal formateados · **0** años sin 4 cifras · **0** `tipo_suceso` fuera de la taxonomía ·
**0** títulos canceléricos · **651** recomendaciones únicas con tipo (0 sin clasificar).

**Nota de coherencia (pendiente):** la hoja `Recomendaciones` trae 651 únicas tras fusionar
288 filas que citaban la misma recomendación en dos páginas del PDF. El visor publica 614,
porque esas salen de la Fase 2 (extraídas del md por LLM) y estas de la tabla determinista
del PDF; difieren en 71 informes (49 con más en el Excel, 22 con más en la DB). Sincronizar
ambas fuentes en una sola queda pendiente.

## Estructura del proyecto

```
era-visor/
├── frontend/index.html   ← el visor completo (mapa + dashboard + tabla), IGN WMTS
│                            Carga en tres tiempos: index.json al arranque →
│                            dashboard.json al abrir esa pestaña →
│                            data/db/detalle/<id>.json al abrir cada ficha
│                            (+ data/db/clima.json UNA vez, al abrir la primera ficha).
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
├── json/ES/           ← un JSON por informe (+ /v3/ con el análisis completo) — 351
├── md/ES/             ← la ÚNICA colección md (la mejorada de Fase 1) — 351
├── pdfs/              ← PDFs originales (fuera de git, ver .gitignore)
├── database/          ← el Excel CIAF de verdad: crudo con cita (data/crudo/),
│                         mecanizado (data/mejorado/), excels base (ciaf_base_*.xlsx),
│                         scripts 01-09 + arnés 99_tests.py
│                         · data/duplicados_excel/ ← los 21 duplicados descartados
│                         · data/ es la ÚNICA fuente de los excels entregables
├── data_antigua/      ← versiones históricas: md originales, JSON de los 21
│                         duplicados, entregables viejos. NADA se borra.
└── docs/              ← estructura del informe, taxonomías, análisis inicial
```

### Dedupe y trazabilidad (2026-09-28)

- El Excel del CIAF traía **21 expedientes con dos documentos**: gana el de más páginas
  e información (`database/scripts/09_dedupe.py`); el descartado se archiva en
  `database/data/duplicados_excel/` y su traza viaja en el propio Excel
  (`n_documentos`, `tipo_documento2`, `descartado_pdf`) y en
  [`data/revision/dedupe-excel.md`](data/revision/dedupe-excel.md).
- **281 informes están en el índice oficial del CIAF**; los 70 de 2006-2007 solo vienen
  de ERA. Marca `indice_oficial` en la DB, columna `en_indice_oficial_ciaf` en los Excel,
  filtro en el visor y listado completo en
  [`data/revision/281-vs-70.md`](data/revision/281-vs-70.md).
- Pipeline de la base: `02_extraer_crudo → 09_dedupe → 03_exportar_excel → 07_normalizar`.
  Arnés: `py database/scripts/99_tests.py` (13 tests, gate).

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

### Capa de vías ADIF, paleta y sello del visor (2026-09-27)

- **Capa de vías ADIF:** el WMS oficial (`ideadif.adif.es/gservices/Tramificacion/wms`)
  responde **403** a cualquier petición — probado por https, http, WFS, geoserver y la
  raíz: toda la subdominio está tras un WAF que bloquea. La capa se dibuja por tanto
  desde `data/vias-adif.geojson`, generado por `scripts/preparar_vias_visor.py` desde el
  trazado oficial `data/adif-tramos.geojson`: Douglas-Peucker a 10 m sobre 604.913
  vértices → **40.157 vértices (1,3 MB, 1.178 líneas)** con `cod_linea`, `provincia`,
  `tipo_red` y `estado`, los dos últimos en el tooltip al pasar el cursor. Carga
  diferida tras el arranque, una sola vez; si falla, el mapa queda como estaba.
  (La primera versión reconstruía la red desde la malla de PKs — un punto cada ~944 m,
  16.058 vértices: se veía recta y con 2,5× menos detalle que el WMS que había antes.)
- **Paleta del dashboard: monocroma azul + gris** (`TONOS` = #1e3a8a → #bfdbfe, `GRIS`
  para la tendencia) con `Chart.defaults` global (texto #64748b, rejillas #eef1f6,
  leyendas con punto). Sin rojos ni ámbar en gráficos: ese color queda para el MAPA,
  donde sí es dato (fallecidos / heridos graves).
- **Sello `datos <versión>`** en la cabecera: si no coincide con el último `VERSION_DATOS`
  publicado, el navegador está sirviendo una copia en caché de la página.
- **Mobile-first medido, no presumido (2026-09-27):** las media queries se reescribieron
  al revés (base = móvil, `min-width` para crecer) y nada se esconde con `display:none`.
  En móvil los filtros entran como **cajón lateral** (botón «☰ Filtros», se cierra al
  cambiar un filtro o tocando fuera), la tabla de 14 columnas se **apila en tarjetas**
  con `data-etiqueta` en cada celda, y desde 700 px vuelve a ser tabla con scroll propio.
  Táctil ≥44 px en pestañas, botones y campos; `font-size: 16px` en los inputs (si no,
  iOS hace zoom al enfocar); `100dvh` en el layout (con `100vh` de reserva).
  **Verificación real con Chrome headless**: 21 comprobaciones (320/360/390/414/768/1024/
  1440 × mapa/dashboard/informes) → **0 desbordes**, 0 errores JS. Capturas en
  `%TEMP%\era-{360,1440}-{informes,dashboard}.png`.

- **Clima histórico en cada ficha (nuevo, 2026-09-27).** Cada informe con coordenadas
  (348/351) muestra el **clima real del día del suceso** y, si el informe publica hora
  (311), también **a la hora exacta**: estado, máx/mín, lluvia y horas de lluvia, viento
  y ráfagas. Fuente: **reanálisis ERA5 vía Open-Meteo Archive** (gratis, sin API key,
  348 consultas en 20 s), precomputado en `data/db/clima.json` por
  `scripts/clima_informes.py` (reanudable: solo consulta huecos; `--refrescar` lo hace
  todo); el visor baja ese JSON **una sola vez** al abrir la primera ficha.
  **Límites honestos**: es reanálisis con resolución ~25 km, no una estación junto a la
  vía — sirve para ver si pudo influir (lluvia, nieve, calor, viento), no como pericial.
  Los 3 informes sin coordenadas no llevan clima: nunca se inventa.
- **Filtro de años táctil**: tiradores de 14 px (lotería con el dedo) → **26 px sobre
  pista de 34 px** con `touch-action:none`, más **dos selects «Desde/Hasta»** para
  elegir el año de un toque y botón «todos». Verificado: 2013–2015 deja 52 de 351 filas
  y «todos» restaura.

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
python scripts/clima_informes.py ES       # 10. clima histórico (ERA5, solo huecos)
python scripts/revisar_json.py DE         # 11. revisor IA
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

- **España: cerrada y auditada (2026-09-28).** Dedupe del Excel aplicado (351 expedientes,
  0 duplicados), marca de índice oficial CIAF (281/70), colecciones únicas (una sola md,
  una sola fuente por JSON), procedencia documentada. Verificación con arnés: 13 tests.
- **Fase 2: Alemania** (452 PDFs detectados), Francia, Italia, Polonia — reusar este mismo
  pipeline de dedupe/auditoría desde el día 1.
- **Traducción** de los informes al castellano en el pipeline (`titulo_normalizado` +
  `idioma_original`), no solo campos cortos.
- **Capas extra:** LTV. *(El clima histórico del día ya está: ERA5 en cada ficha.)*
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