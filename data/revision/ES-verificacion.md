# Informe de verificación — ES

> `scripts/verificar_todo.py` · 2026-09-27 11:48 · **APTO** · 2 avisos · 15 checks OK

## 1. Integridad de la cadena PDF ↔ md ↔ json ↔ DB

- **[OK]** pdf→md: 372/372 PDFs con .md; sin md: ninguno
- **[OK]** md→json: 372 .md estructurados en json
- **[OK]** json→v3: 372 json con análisis v3
- **[OK]** DB→json: 351 registros DB con json origen
- **[OK]** json→DB: 372 json estructurados presentes en la DB (21 dobles fusionados)

## 2. Duplicados por contenido (md5 de PDFs)

- **[OK]** md5: 372 PDFs, 0 duplicados por contenido

## 3. Salud de los PDFs

- **[OK]** magic bytes: 372 PDFs válidos (los bloqueos HTML llegarían aquí)
- **[OK]** tamaño: todos ≥ 10 KB

## 4. Salud del índice de la DB

- **[OK]** ids únicos: 351 entradas
- **[OK]** fantasmas: index ES == reports (351), 0 fantasmas
- **[OK]** campos index: fecha/título/fallecidos OK
- **[OK]** víctimas v3→DB: las consecuencias v3 mandan en todos los registros
- **[OK]** 1 registro por expediente: 351 expedientes, 0 duplicados
- **[AVISO]** coords gemelas: 6 legítimas; SOSPECHOSAS 2 (PK distintos, misma coord): 0007/2012(PK 109+810)≡0018/2011(PK 110+000); 0006/2012(PK 378+049)≡0013/2009(PK 378,130)

## 5. Auditoría geográfica — los mal geolocalizados, SIEMPRE a la vista

- **[OK]** veredictos: 351 informes auditados: bien=315 · sin_coords=36
- **[AVISO]** provincia: 19 con provincia declarada ≠ provincia de la red

**MAL GEOLocalIZADOS: ninguno.**


**DUDOSOS: ninguno.**


## 6. Cache-busting del frontend

- **[OK]** VERSION_DATOS: 2026-09-27-1 cubre la DB (2026-09-27)
