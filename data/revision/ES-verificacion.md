# Informe de verificación — ES

> `scripts/verificar_todo.py` · 2026-09-07 22:46 · **APTO** · 4 avisos · 13 checks OK

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
- **[AVISO]** coords gemelas: 6 legítimas; SOSPECHOSAS 1 (PK distintos, misma coord): 0006/2012(PK 378+049)≡0013/2009(PK 378,130)

## 5. Auditoría geográfica — los mal geolocalizados, SIEMPRE a la vista

- **[AVISO]** veredictos: 349 informes auditados: bien=299 · duda=2 · mal=9 · sin_coords=39
- **[AVISO]** provincia: 20 con provincia declarada ≠ provincia de la red

**MAL GEOLocalIZADOS — 9 informes** (verificar contra el PDF original):

| Informe | Provincia | PK | Línea | A la vía | Motivo |
|---|---|---|---|---|---|
| `ES-ES 25.01.2016 170331-160125-IF-CIAF` | Alicante | — | 336 El Reguerón a Alacant  | 987 m | cae sobre OTRA vía: a 948 m del tramo 022200070 (línea 220), la declarada 336 está a 416640 m |
| `ES-ES 18.11.2014 151124-141118-IF-CIAF` | Tarragona | PK 0+571 | Línea 622 Aguja Clasif. PK | 0 m | cae sobre OTRA vía: a 0 m del tramo 022000440 (línea 200), la declarada 622 está a 21679 m |
| `ES-ID-211207-290408-CIAF[1]` | Tarragona | 263,600 | 600 Valencia-San Vicente C | 0 m | cae sobre OTRA vía: a 0 m del tramo 110800150 (línea 080), la declarada 600 está a 409467 m |
| `ES-ID-280207-190707-DGF` | Tarragona | 13,550 | Línea 600 Valencia Norte - | 0 m | cae sobre OTRA vía: a 0 m del tramo 022000460 (línea 200), la declarada 600 está a 16210 m |
| `ES-IF-060910-290711-CIAF` | Badajoz | 24+420 | 510 Aljucén - Cáceres | 0 m | cae sobre OTRA vía: a 0 m del tramo 045140020 (línea 514), la declarada 510 está a 65811 m |
| `ES-IF-090212-271112-CIAF` | Barcelona | 28+158 | 276 Maçanet-Massanes a Bif | 0 m | cae sobre OTRA vía: a 0 m del tramo 022220010 (línea 222), la declarada 276 está a 14427 m |
| `ES-IF-201208-210409-CIAF` | Tarragona | 263,208 | 600 Valencia Nord - Sant V | 0 m | cae sobre OTRA vía: a 0 m del tramo 126400020 (línea 640), la declarada 600 está a 7957 m |
| `ES-IF-240608-281108-CIAF` | Barcelona | 26,100 | 276 Barcelona Sagrera a Ma | 0 m | cae sobre OTRA vía: a 0 m del tramo 022220010 (línea 222), la declarada 276 está a 12606 m |
| `ES-IF_081012_250613_CIAF` | Huesca | PK 25+100 | Línea 200 Madrid Chamartín | 0 m | cae sobre OTRA vía: a 0 m del tramo 022040020 (línea 204), la declarada 200 está a 23125 m |


**DUDOSOS — 2 informes** (verificar contra el PDF original):

| Informe | Provincia | PK | Línea | A la vía | Motivo |
|---|---|---|---|---|---|
| `ES-ES IF_060613_281014_CIAF` | Zaragoza | — | 060 Bifurcación Cambiador  | 11 m | cae sobre OTRA vía: a 11 m del tramo 022000260 (línea 200), la declarada 060 está a 1475 m |
| `ES-IF-271211-250912-CIAF` | Zaragoza | — | 060 Bifurcación Cambiador  | 11 m | cae sobre OTRA vía: a 11 m del tramo 022000260 (línea 200), la declarada 060 está a 1475 m |


## 6. Cache-busting del frontend

- **[OK]** VERSION_DATOS: 2026-09-07-2 cubre la DB (2026-09-07)
