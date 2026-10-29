# Informes CIAF — .md regenerados (v2)

351 informes de investigación de la CIAF (Comisión de Investigación de Accidentes Ferroviarios),
regenerados desde los **PDF originales** (fuente oficial ERA + copias locales verificadas por md5)
con un conversor determinista propio (PyMuPDF). Sustituyen a los de `md/ES/`, que salían desordenados
del extractor antiguo.

- **Verbatim**: el texto no se modifica; solo se excluyen rótulos de cabecera/pie repetidos
  (contados en el frontmatter de cada fichero) y las tablas se vuelcan como filas pipe.
- **Cadena de custodia**: `md5_pdf` + `url_oficial` en el frontmatter de cada md, contrastados
  con ERA (373/374 idénticos bit a bit; ver manifiesto del proyecto de análisis).
- **Determinista**: mismo PDF + misma versión de PyMuPDF → mismo .md.
- **Fecha de generación**: 2026-10-29 · Origen: PDFs ERA 2006–2025.
- Un informe escaneado (`ID_230507_140907`) recupera sus páginas del OCR del pipeline antiguo
  (`paginas_ocr_antiguo: 7` en su frontmatter).

Hecho con ❤️ por David Antizar
