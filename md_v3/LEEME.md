# md_v3 — Informes CIAF regenerados desde los PDF originales (extractor tipográfico)

**Fecha:** 2026-10-29 · **351 informes** · determinista, sin LLM.

## Qué son

Markdown regenerados directamente de los **PDF originales de la CIAF** leyendo la
**estructura tipográfica** del documento (tamaño/negrita de fuente en modo `dict` de
PyMuPDF), no el texto plano. Por eso:

- **Orden original del índice**: los encabezados `#`/`##`/`###` siguen la jerarquía
  tipográfica del PDF (títulos de sección y subsección tal como declara el documento).
- **Sin ruido de página**: membrete («MINISTERIO…»), rótulos «Pág. N de N» y marcos de
  plantilla se eliminan por detección de repetición; cada página arranca con
  `## Página N` (línea uniforme, fácil de filtrar).
- **Portada íntegra**: la primera página nunca se re-jerarquiza ni se limpia.

## Verbatim y trazabilidad

- Cada línea emitida se verifica como **substring literal del texto del PDF**
  (normalizando espacios): el frontmatter lleva `verbatim_fallos: 0` en los 351.
- El frontmatter lleva `md5_pdf` (fichero fuente), `cadena_custodia: ok` (verificado
  bit a bit contra las descargas de ERA: 373/377 idénticos) y metadatos del conversor.
- Un informe (`ID_230507_140907`) es un **PDF escaneado** sin capa de texto: sus 7
  páginas se rescatan verbatim del OCR antiguo (`paginas_ocr_antiguo: 7`).

## Determinismo

El mismo PDF produce siempre el mismo md (conversor por reglas de fuente, sin heurísticas
de LLM). Regenerado dos veces → md5 idéntico.

## Descartados

24 duplicados se apartan en local (`_duplicados_descartados/`) y **no** se publican.

---
Hecho con ❤️ por David Antizar
