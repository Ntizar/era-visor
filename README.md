# ERA-Visor

Visor europeo de informes de investigación de accidentes ferroviarios. Convierte los
PDF oficiales (ERA/eRAIL + organismos nacionales como el CIAF) en una base de datos
plana y filtrable, sobre un mapa con la red ferroviaria real de ADIF.

Hecho con ❤️ por David Antizar

---

## Qué hace

1. **Descarga** los informes oficiales por país (scrape de ERA + PDFs originales).
2. **Extrae** el texto (PyMuPDF, OCR solo cuando hace falta) a `.md` legible.
3. **Estructura** cada `.md` a un JSON normalizado con LLM (`qwen3.8-flash`).
4. **Enriquece** con taxonomía oficial v2: subsistema, sistema de protección
   (ASFA/ERTMS/LZB), tipo de red, explotación, precursores, mitigaciones, factores
   humanos, meteorología.
5. **Geolocaliza** cada informe SOBRE la vía: PK + línea → interpolación en la red
   ADIF (WFS Tramificación) o PK teórico más cercano.
6. **Revisa** todo automáticamente: distancia real a la vía, provincia vs red ADIF,
   y un revisor IA que revalida cada JSON contra su informe original.
7. **Visualiza**: mapa con vías ADIF, dashboard con 12+ gráficos, tabla filtrable,
   ficha de detalle completa, export a Excel.

## Estructura del proyecto

```
era-visor/
├── frontend/
│   └── index.html        ← el visor completo (mapa + dashboard + tabla)
├── scripts/              ← pipeline, en orden de ejecución
│   ├── scrape_pais.py        1. descubre los informes de un país en ERA
│   ├── descargar_pdfs.py     2. baja los PDFs (backoff 429, cortesía 8s)
│   ├── extraer_pais.py       3. PDF → .md (PyMuPDF; OCR solo si hace falta)
│   ├── estructurar_pais.py   4. .md → .json (LLM, schema v1)
│   ├── enriquecer_ia.py      5. .json → campos v2 (taxonomía KAIZEN)
│   ├── geocodificar_via.py   6. PK+línea → coordenadas SOBRE la vía ADIF
│   ├── revisar_localizacion.py  7. auditoría: distancia a vía, provincia vs ADIF
│   ├── revisar_json.py       8. revisor IA: revalida cada JSON contra su .md
│   ├── importar_ciaf.py      (helper) importa los 269 informes CIAF verificados
│   ├── extraer_erail.py      (helper) Excel eRAIL → JSON por país
│   ├── cruce_erail.py        (helper) cruza eRAIL ↔ PDFs descargados
│   └── consolidar.py         9. json/* → data/db/ (dedupe: CIAF > LLM)
├── data/
│   ├── pdf-manifest/     ← qué PDFs hay por país (ES.json)
│   ├── erail/            ← Excel eRAIL convertido
│   ├── cruce/            ← cruce eRAIL ↔ PDF
│   ├── adif-*.geojson    ← red ADIF: tramos y PK teóricos (WFS IDEADIF)
│   ├── revision/         ← informes de auditoría (veredictos de localización)
│   └── db/               ← SALIDA FINAL: index.json + reports/ES.json + recs/
├── json/ES/              ← un JSON por informe (fuente de la DB)
├── md/ES/                ← un .md por informe (texto extraído del PDF)
├── pdfs/ES/              ← PDFs originales (no se suben si pesan; enlazados)
└── docs/                 ← estructura del informe, taxonomías KAIZEN
```

## Cómo usarlo

### Ver el visor

```bash
cd era-visor
python -m http.server 8765
# abre http://localhost:8765/frontend/index.html
```

### Procesar un país nuevo (ej. Alemania)

```bash
python scripts/scrape_pais.py DE          # descubre informes
python scripts/descargar_pdfs.py DE       # baja PDFs (lento: cortesía 8s)
python scripts/extraer_pais.py DE         # PDF → MD
python scripts/estructurar_pais.py DE     # MD → JSON (LLM)
python scripts/enriquecer_ia.py DE        # campos v2 (LLM)
python scripts/geocodificar_via.py DE     # coords sobre la vía
python scripts/revisar_localizacion.py DE # auditoría de localización
python scripts/revisar_json.py DE         # revisor IA
python scripts/consolidar.py DE           # → data/db/
```

Todo es **reanudable**: si se corta, relanza el mismo comando y continúa donde estaba.

### Comandos útiles

```bash
python scripts/consolidar.py ES           # reconstruir la DB desde json/
python scripts/revisar_localizacion.py ES # radiografía de localización
python scripts/revisar_json.py ES --limite 20   # revisor IA sobre 20 informes
```

## El schema del JSON

Cada informe (`json/ES/<id>.json`) tiene:

| Campo | Qué es | Ejemplo |
|---|---|---|
| `id` | identificador estable | `ES-190628-120817-IF-SN_CIAF` |
| `titulo`, `fecha`, `hora` | del informe | `2017-08-12` |
| `expediente` | referencia oficial | `0062/2007` |
| `tipo`, `tipo_categoria` | suceso normalizado | `descarrilamiento` |
| `provincia`, `estacion`, `pk`, `linea` | localización textual | `P.K. 429,825` |
| `lat`, `lng`, `metodo_geo` | coordenadas sobre vía + método | `via_pk` |
| `fallecidos`, `heridos_graves` | víctimas (eRAIL manda) | |
| `trenes` | implicados con operador | |
| `resumen`, `descripcion`, `causa_directa`, `conclusiones` | textos | |
| `recomendaciones` | de seguridad emitidas | |
| `tags` | conceptos clave | |
| **v2 (IA)**: `subsistema`, `sistema_proteccion`, `tipo_red`, `explotacion`, `precursores`, `mitigaciones`, `factores_humanos`, `meteorologia`, `circulation_type`, `fase_ciclo_vida` | taxonomía oficial | `ERTMS`, `Degradada` |

## Reglas del proyecto

1. **La DB es plana y sin imágenes.** Los PDFs NUNCA van dentro: se enlazan
   (`url_pdf`). Los textos largos viven en `md/` para RAG futuro.
2. **CIAF gana el dedupe**: cuando un expediente tiene versión CIAF (verificada)
   y versión LLM, gana CIAF, pero los campos v2 del LLM se FUSIONAN.
3. **Todo en castellano** (repos, scripts, comentarios, UI).
4. **No inventar datos**: si el LLM no encuentra un dato en el texto, `null`.
   Las víctimas siempre de eRAIL, nunca estimadas.
5. **Cortesía con ERA**: 8s entre peticiones; ante 429, backoff 120s × intento.
6. **Geolocalización con veredicto**: cada punto lleva `metodo_geo`
   (`via_pk` interpolado > `via_pkteorico` > `nominatim`) y pasa auditoría
   de distancia a vía (`data/revision/`).
7. **Un solo proceso en background a la vez** (las escrituras colisionan).
8. **Reanudable siempre**: todos los scripts comprueban qué ya está hecho.

## Estado actual (ES)

- 374 PDFs (2006-2025) · 374 .md · ~640 JSON (269 CIAF verificados + LLM)
- DB consolidada: 318 informes · 250 bien localizados (79%), 31 dudosos,
  23 mal, 14 sin coords → el revisor IA los corrige y reconsolida
- Enriquecimiento v2 en curso (~180/374)
- Frontend: mapa con vías ADIF (WMS), doble slider de años, 4 filtros v2,
  dashboard con regresión lineal, export Excel

## Hoja de ruta

- [ ] Cerrar ES al 100%: OCR del informe pendiente + revisor IA completo
- [ ] Fase 2: Alemania (452 PDFs ya detectados), Francia, Italia, Polonia
- [ ] Capas extra: estaciones (IGN), meteorología del día (Open-Meteo histórico)
- [ ] Traducción ES/EN de campos cortos (qwen batch)
- [ ] API JSON pública (GitHub Pages ya sirve `data/db/`)
