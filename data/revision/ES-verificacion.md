# Informe de verificación — ES

> `scripts/verificar_todo.py` · 2026-09-08 09:58 · **APTO** · 3 avisos · 14 checks OK

## 1. Integridad de la cadena PDF ↔ md ↔ json ↔ DB

- **[OK]** pdf→md: 372/372 PDFs con .md; sin md: ninguno
- **[OK]** md→json: 371 .md estructurados en json
- **[AVISO]** OCR pendiente: 1 escaneados sin capa de texto, sin estructurar: ID_230507_140907
- **[OK]** json→v3: 371 json con análisis v3
- **[OK]** DB→json: 349 registros DB con json origen

## 2. Duplicados por contenido (md5 de PDFs)

- **[OK]** md5: 372 PDFs, 0 duplicados por contenido

## 3. Salud de los PDFs

- **[OK]** magic bytes: 372 PDFs válidos (los bloqueos HTML llegarían aquí)
- **[OK]** tamaño: todos ≥ 10 KB

## 4. Salud del índice de la DB

- **[OK]** ids únicos: 349 entradas
- **[OK]** fantasmas: index ES == reports (349), 0 fantasmas
- **[OK]** campos index: fecha/título/fallecidos OK
- **[OK]** víctimas v3→DB: las consecuencias v3 mandan en todos los registros
- **[OK]** 1 registro por expediente: 349 expedientes, 0 duplicados
- **[AVISO]** coords gemelas: 6 legítimas; SOSPECHOSAS 3 (PK distintos, misma coord): 0063/2007(PK 263,600)≡0074/2008(PK 263,208); 0007/2012(PK 109+810)≡0018/2011(PK 110+000); 0006/2012(PK 378+049)≡0013/2009(PK 378,130)

## 5. Auditoría geográfica — los mal geolocalizados, SIEMPRE a la vista

- **[OK]** veredictos: 349 informes auditados: bien=314 · sin_coords=35
- **[AVISO]** provincia: 19 con provincia declarada ≠ provincia de la red

**MAL GEOLocalIZADOS: ninguno.**


**DUDOSOS: ninguno.**


## 6. Cache-busting del frontend

- **[OK]** VERSION_DATOS: 2026-09-08-3 cubre la DB (2026-09-08)
