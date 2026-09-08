# Informe de verificación — ES

> `scripts/verificar_todo.py` · 2026-09-08 08:43 · **APTO** · 4 avisos · 13 checks OK

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

- **[AVISO]** veredictos: 349 informes auditados: bien=307 · duda=4 · mal=3 · sin_coords=35
- **[AVISO]** provincia: 19 con provincia declarada ≠ provincia de la red

**MAL GEOLocalIZADOS — 3 informes** (verificar contra el PDF original):

| Informe | Provincia | PK | Línea | A la vía | Motivo |
|---|---|---|---|---|---|
| `ES-IF-060910-290711-CIAF` | Badajoz | 24+420 | 510 Aljucén - Cáceres | 16606 m | cae sobre OTRA vía: a 16328 m del tramo 045200120 (línea 520), la declarada 510 está a 34201 m |
| `ES-ES 18.11.2014 151124-141118-IF-CIAF` | Tarragona | PK 0+571 | Línea 622 Aguja Clasif. PK | 2421 m | cae sobre OTRA vía: a 2404 m del tramo 022100140 (línea 210), la declarada 622 está a 2438 m |
| `ES-ES 25.01.2016 170331-160125-IF-CIAF` | Alicante | 435,900 | 336 El Reguerón a Alacant  | 987 m | cae sobre OTRA vía: a 948 m del tramo 022200070 (línea 220), la declarada 336 está a 416640 m |


**DUDOSOS — 4 informes** (verificar contra el PDF original):

| Informe | Provincia | PK | Línea | A la vía | Motivo |
|---|---|---|---|---|---|
| `ES-ID-211207-290408-CIAF[1]` | Tarragona | 263,600 | 600 Valencia-San Vicente C | 1709 m | cae sobre OTRA vía: a 1668 m del tramo 036000157 (línea 600), la declarada 600 está a 1668 m |
| `ES-IF-201208-210409-CIAF` | Tarragona | 263,208 | 600 Valencia Nord - Sant V | 1709 m | cae sobre OTRA vía: a 1668 m del tramo 036000157 (línea 600), la declarada 600 está a 1668 m |
| `ES-ES IF_060613_281014_CIAF` | Zaragoza | — | 060 Bifurcación Cambiador  | 11 m | cae sobre OTRA vía: a 11 m del tramo 022000260 (línea 200), la declarada 060 está a 1475 m |
| `ES-IF-271211-250912-CIAF` | Zaragoza | — | 060 Bifurcación Cambiador  | 11 m | cae sobre OTRA vía: a 11 m del tramo 022000260 (línea 200), la declarada 060 está a 1475 m |


## 6. Cache-busting del frontend

- **[OK]** VERSION_DATOS: 2026-09-08-1 cubre la DB (2026-09-08)
