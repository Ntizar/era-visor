# Informe del corpus — accidentes ferroviarios de la ERA en castellano

Generado por `scripts/informe.py` el 2026-11-21 a partir del disco. Ningún dato de este documento está escrito a mano: si algo no existe, aparece «—».

## Resumen

| Concepto | Valor |
|---|---|
| PDF publicados por ERA (manifiestos) | **4015** |
| PDF en disco | 4013 |
| MD originales extraídos | **3963 (98.7 %)** |
| MD en castellano | **3470 (87.6 % de los extraídos)** |
| · verificados ok | 2767 |
| · con páginas a repasar | 703 |
| · traducciones vacías o truncadas | 0 |
| Informes revisados por IA (deepseek) | 316 |
| PDF escaneados sin capa de texto | 169 |
| · recuperados por OCR auditado | 159 |

## Por país

| Código | País | PDF publ. | PDF disco | MD | MD-es | ok | a repasar | vacías | Rev. IA | Fidelidad | OCR | Conf. OCR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **AT** | Austria | 184 | 184 | 184 | 184 | 139 | 45 | 0 | 0 | — | — | — |
| **BE** | Bélgica | 112 | 112 | 112 | 112 | 106 | 6 | 0 | 11 | 92.2 | 1 | 82.3 |
| **BG** | Bulgaria | 56 | 56 | 56 | 56 | 50 | 6 | 0 | 56 | 95.6 | 4 | 68.2 |
| **CH** | Suiza | 8 | 8 | 8 | 8 | 7 | 1 | 0 | 8 | 96.1 | — | — |
| **CZ** | Chequia | 577 | 577 | 579 | 570 | 221 | 349 | 0 | 0 | — | — | — |
| **DE** | Alemania | 368 | 366 | 366 | 364 | 346 | 18 | 0 | 0 | — | — | — |
| **DK** | Dinamarca | 146 | 146 | 120 | 119 | 115 | 4 | 0 | 0 | — | — | — |
| **EE** | Estonia | 13 | 13 | 13 | 13 | 7 | 6 | 0 | 13 | 87.2 | — | — |
| **EL** | Grecia | 3 | 3 | 3 | 3 | 2 | 1 | 0 | 3 | 97.3 | — | — |
| **ES** | España | 374 | 375 | 354 | 705 | 698 | 7 | 0 | 0 | — | — | — |
| **FI** | Finlandia | 312 | 312 | 311 | 295 | 229 | 66 | 0 | 0 | — | 63 | 93.5 |
| **FR** | Francia | 118 | 118 | 118 | 24 | 18 | 6 | 0 | 0 | — | 3 | 90.1 |
| **HR** | Croacia | 107 | 107 | 106 | 106 | 37 | 69 | 0 | 11 | 88.5 | 4 | 93.5 |
| **HU** | Hungría | 495 | 495 | 493 | 292 | 261 | 31 | 0 | 0 | — | — | — |
| **IE** | Irlanda | 51 | 51 | 51 | 51 | 51 | 0 | 0 | 51 | 96.6 | — | — |
| **IT** | Italia | 94 | 94 | 94 | 94 | 91 | 3 | 0 | 9 | 92.5 | 19 | 89.1 |
| **LT** | Lituania | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 6 | 46.5 | 2 | 94.7 |
| **LU** | Luxemburgo | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 4 | 94.3 | — | — |
| **LV** | Letonia | 26 | 26 | 26 | 26 | 25 | 1 | 0 | 26 | 96.2 | — | — |
| **NL** | Países Bajos | 21 | 21 | 21 | 21 | 9 | 12 | 0 | 21 | 94.2 | — | — |
| **NO** | Noruega | 168 | 168 | 168 | 0 | 0 | 0 | 0 | 0 | — | 1 | 70.0 |
| **PL** | Polonia | 128 | 128 | 128 | 2 | 2 | 0 | 0 | 0 | — | 28 | 88.5 |
| **PT** | Portugal | 57 | 57 | 57 | 57 | 42 | 15 | 0 | 3 | 64.4 | 3 | 92.2 |
| **RS** | Serbia | 57 | 57 | 56 | 56 | 43 | 13 | 0 | 7 | 96.4 | — | — |
| **SE** | Suecia | 88 | 88 | 88 | 88 | 80 | 8 | 0 | 9 | 94.1 | 1 | 91.8 |
| **SI** | Eslovenia | 39 | 39 | 39 | 39 | 11 | 28 | 0 | 39 | 98.4 | 28 | 92.6 |
| **SK** | Eslovaquia | 39 | 39 | 39 | 39 | 37 | 2 | 0 | 39 | 92.2 | 2 | 87.9 |
| **UK** | Reino Unido | 364 | 363 | 363 | 136 | 130 | 6 | 0 | 0 | — | — | — |

## Cómo se ha hecho cada cosa (método y garantías)

**Extracción (PDF → MD).** `convertir_md_pais.py` lee el PDF en modo tipográfico (PyMuPDF): encabezados por tamaño de fuente, membrete repetido eliminado, tablas reales en pipes. Cada línea emitida se verifica contra el texto del PDF y el número de fallos queda en el frontmatter (`verbatim_fallos`). Si una página no tiene capa de texto se declara (`escaneado: true`, `paginas_sin_texto`) y no se rellena a mano.

**OCR (solo escaneados).** `ocr_escaneados.py` con **Tesseract 5.4 + tessdata_best a 300 dpi** e idioma por país. Se registra motor y versión, idiomas, páginas, páginas vacías, **confianza media y mínima por palabra**, md5 del PDF y fecha, en `data/ocr/<CC>.json`. Por debajo de 70 de confianza el informe se marca para revisión manual.

**Traducción.** `traducir_md_es.py` con `qwen3.8-flash` (`enable_thinking: false`), en bloques de ~7 000 caracteres, con instrucciones de fidelidad literal, tablas celda a celda y secciones canónicas. Cada bloque se **verifica**: marcadores de página, cifras largas (≥3 dígitos) y cortas, fechas normalizadas y ratio de longitud. Si falla hay un reintento correctivo; si sigue fallando, el informe queda `verificacion: revisar` con el motivo escrito.

**Reparación.** `--reparar` re-traduce **solo las páginas que fallan**, no el informe entero. `--vacios` detecta traducciones vacías o truncadas (menos del 30 % del original) y las rehace: pasa cuando el MD se tradujo antes de tener texto (escaneados sin OCR).

**Original bilingüe.** Algunos informes (Portugal) publican dos idiomas intercalados línea a línea; la traducción correcta colapsa el duplicado y sale a la mitad de caracteres. Se detecta por línea y se compara contra el idioma principal para no marcar falsos fallos.

**Revisión IA.** `revisar_md_es.py` con `deepseek-v4-pro`: compara original y castellano página a página (6 muestras por informe) y devuelve fidelidad 0-100, omisiones, invenciones y cifras mal. Umbral 85. Una página sin dictamen no cuenta como fallo: se declara.

**Custodia.** Cada MD lleva `pdf`, `md5_pdf`, `url_oficial`, `paginas`, `chars`, fecha y generador. Cada md-es lleva además `md_origen`, `md5_origen`, modelo usado y veredicto. Los PDF no van al repositorio (`pdfs/` está ignorado): son reproducibles desde el manifiesto.

**Concurrencia y cola compartida.** 5 llamadas simultáneas de día y 6 de 00:00 a 06:00, medido: ~60 k caracteres/min. Traducción y revisión nunca a la vez.
