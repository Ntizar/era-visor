# ERA Visor — Visor europeo de accidentes ferroviarios

![Estado](https://img.shields.io/badge/Fase-Espa%C3%B1a-blue) ![Informes](https://img.shields.io/badge/Informes-426-green) ![An%C3%A1lisis%20IA](https://img.shields.io/badge/An%C3%A1lisis%20IA-351-orange)

Visor y base de datos de informes de investigación de accidentes ferroviarios. Convierte los
PDF oficiales (ERA/eRAIL + organismos nacionales como el CIAF) en una base de datos plana,
filtrable y auditada, sobre un mapa con la red ferroviaria real de ADIF.

**Ver el visor:** <https://ntizar.github.io/era-visor/>

Hecho con ❤️ por David Antizar

## Qué hace

1. **Descarga** los informes oficiales por país (scrape de ERA + PDFs originales).
2. **Extrae** el texto (PyMuPDF, OCR solo cuando hace falta) a `.md` legible.
3. **Estructura** cada `.md` a un JSON normalizado con LLM (`qwen3.8-flash`).
4. **Enriquece** con taxonomía v2: subsistema, sistema de protección (ASFA/ERTMS/LZB),
   tipo de red, explotación, precursores, mitigaciones, factores humanos, meteorología.
5. **Extrae el análisis v3 completo**: hechos narrativos limpios (sin índices del PDF),
   cronología minuto a minuto, infraestructura, personal implicado, material rodante,
   causas (directa/contribuyentes/sistémicas), consecuencias, lecciones y recomendaciones.
   Anti-invención: si el dato no está en el informe, es `null`.
6. **Geolocaliza** cada informe sobre la vía: PK + línea → interpolación en la red ADIF
   (WFS Tramificación); si no hay PK, por estación (IGN, 3.000 estaciones); nunca inventa
   coordenadas.
7. **Audita** todo automáticamente: distancia real a la vía, provincia vs red ADIF, y un
   revisor IA que revalida cada JSON contra su informe original.
8. **Visualiza**: mapa con vías ADIF, dashboard con 12+ gráficos, tabla filtrable,
   ficha de detalle completa, export a Excel.

## Estado actual (España)

| Métrica | Valor |
|---|---|
| Informes en la DB | 426 (2006-2025, CIAF + ERA) |
| Con análisis v3 completo (cronología, infraestructura, lecciones…) | 351 |
| Con taxonomía v2 | 352 |
| Localización auditada | 361 bien · 29 dudosos · 1 mal · 35 sin coords |
| Sobre la vía ADIF (interpolación PK) | 345 + 129 PK teórico |
| Por estación IGN | 47 |

Residuos conocidos: 35 informes sin PK ni estación en el PDF (no se inventa localización),
1 informe pendiente de OCR, 1 con error de API persistente.

## Estructura del proyecto

```
era-visor/
├── frontend/
│   └── index.html        ← el visor completo (mapa + dashboard + tabla)
├── scripts/              ← pipeline, en orden de ejecución
│   ├── scrape_pais.py           1. descubre los informes de un país en ERA
│   ├── descargar_pdfs.py        2. baja los PDFs (backoff 429, cortesía 8s)
│   ├── extraer_pais.py          3. PDF → .md (PyMuPDF; OCR solo si hace falta)
│   ├── estructurar_pais.py      4. .md → .json (LLM, schema v1)
│   ├── enriquecer_ia.py         5. .json → campos v2 (taxonomía)
│   ├── extraer_completo.py      6. análisis v3: hechos, cronología, infraestructura…
│   ├── geocodificar_via.py      7. PK+línea → coordenadas SOBRE la vía ADIF
│   ├── geocodificar_estacion.py 7b. sin PK → estación IGN (matcher estricto)
│   ├── revisar_localizacion.py  8. auditoría: distancia a vía, provincia vs ADIF
│   ├── revisar_json.py          9. revisor IA: revalida cada JSON contra su .md
│   ├── importar_ciaf.py         (helper) importa los 269 informes CIAF verificados
│   ├── extraer_erail.py         (helper) Excel eRAIL → JSON por país
│   ├── cruce_erail.py           (helper) cruza eRAIL ↔ PDFs descargados
│   └── consolidar.py            10. json/* → data/db/ (dedupe: CIAF > LLM, fusiona v2/v3)
├── data/
│   ├── pdf-manifest/     ← qué PDFs hay por país (ES.json)
│   ├── erail/            ← Excel eRAIL convertido
│   ├── cruce/            ← cruce eRAIL ↔ PDF
│   ├── adif-*.geojson    ← red ADIF: tramos y PK teóricos (WFS IDEADIF)
│   ├── revision/         ← informes de auditoría (veredictos de localización)
│   └── db/               ← SALIDA FINAL: index.json + reports/ES.json + recs/
├── json/ES/              ← un JSON por informe (+ json/ES/v3/ con el análisis completo)
├── md/ES/                ← un .md por informe (texto extraído del PDF)
└── docs/                 ← estructura del informe, taxonomías
```

## Cómo usarlo

### Ver el visor

En línea: <https://ntizar.github.io/era-visor/> · En local:

```shell
cd era-visor
python -m http.server 8765
# abre http://localhost:8765/frontend/index.html
```

### Procesar un país nuevo (ej. Alemania)

```shell
python scripts/scrape_pais.py DE          # descubre informes
python scripts/descargar_pdfs.py DE       # baja PDFs (lento: cortesía 8s)
python scripts/extraer_pais.py DE         # PDF → MD
python scripts/estructurar_pais.py DE     # MD → JSON (LLM)
python scripts/enriquecer_ia.py DE        # campos v2 (LLM)
python scripts/extraer_completo.py DE     # análisis v3 (LLM)
python scripts/geocodificar_via.py DE     # coords sobre la vía
python scripts/geocodificar_estacion.py DE # o por estación
python scripts/revisar_localizacion.py DE # auditoría de localización
python scripts/revisar_json.py DE         # revisor IA
python scripts/consolidar.py DE           # → data/db/
```

Todo es **reanudable**: si se corta, relanza el mismo comando y continúa donde estaba.

## El schema del JSON

Cada informe (`json/ES/<id>.json`, con el análisis completo en `json/ES/v3/<id>.json`):

| Campo | Qué es |
|---|---|
| `id`, `titulo`, `fecha`, `hora` | identificación del informe |
| `expediente` | referencia oficial (`0062/2007`) |
| `provincia`, `estacion`, `pk`, `linea` | localización textual |
| `lat`, `lng`, `metodo_geo` | coordenadas (`via_pk`, `via_pkteorico`, `estacion_ign`, `previa`) |
| `fallecidos`, `heridos_graves`, `danos_materiales`, `gravedad` | consecuencias |
| `subsistema`, `sistema_proteccion`, `tipo_red`, `explotacion` | taxonomía v2 |
| `precursores`, `mitigaciones`, `factores_humanos`, `meteorologia` | causas y contexto v2 |
| `v3.hechos` | narrativa limpia del suceso (2-4 párrafos, sin índice del PDF) |
| `v3.cronologia` | eventos minuto a minuto |
| `v3.infraestructura` | señalización, tipo de vía, velocidad máx, ancho, electrificación |
| `v3.personal`, `v3.trenes`, `v3.material_rodante` | implicados |
| `v3.causas` | directa, contribuyentes, sistémicas |
| `v3.lecciones`, `v3.recomendaciones` | con destinatario |
| `url_pdf` | enlace al PDF original (los PDFs nunca van en la DB) |

## Lecciones aprendidas (pipeline)

- **No cruzar por expediente sin año** (`50` ≠ `0050/2009`): corrupción masiva de datos.
- **Matcher estricto o abstención**: mejor sin coordenada que mal puesta (la contención
  difusa por nombre puso informes de media España en Salamanca).
- **PKs con notación variada**: `429,825` (decimal), `368+925` (km+m), `124/573` (CIAF,
  barra decimal) — el parser debe cubrir los tres.
- **El LLM no inventa**: anti-invención estricta; `null` si el dato no está en el informe.
- **El revisor IA paga**: 2.413 correcciones en 370 JSON en una pasada; re-ejecutable
  siempre.

## Despliegue

GitHub Pages vía workflow moderno (`.github/workflows/pages.yml`, `actions/deploy-pages@v4`),
deploy directo desde `main`. La DB es JSON estático servido tal cual.

## Hoja de ruta

- **Fase 1 (actual): España al 100%** — pulir los 29 dudosos y los 35 sin coords,
  OCR del informe pendiente.
- Fase 2: Alemania (452 PDFs detectados), Francia, Italia, Polonia.
- Capas extra: meteorología del día (Open-Meteo histórico), LTV.
- Traducción de campos cortos EN→ES (batch).
- API JSON pública (Pages ya sirve `data/db/`).

## Licencia

Datos: fuentes oficiales (ERA/eRAIL, CIAF, ADIF, IGN — CC BY 4.0). Código: libre.
Hecho con ❤️ por David Antizar
