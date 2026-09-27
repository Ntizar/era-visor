# Informe de verificación — ES

> `scripts/verificar_todo.py` · 2026-09-27 14:45 · **APTO** · 3 avisos · 14 checks OK

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
- **[AVISO]** coords gemelas: 9 legítimas; SOSPECHOSAS 2 (PK distintos, misma coord): 0007/2012(PK 109+810)≡0018/2011(PK 110+000); 0006/2012(PK 378+049)≡0013/2009(PK 378,130)

## 5. Auditoría geográfica — los mal geolocalizados, SIEMPRE a la vista

- **[AVISO]** veredictos: 351 informes auditados: bien=344 · mal=4 · sin_coords=3
- **[AVISO]** provincia: 21 con provincia declarada ≠ provincia de la red

**MAL GEOLocalIZADOS — 4 informes** (verificar contra el PDF original):

| Informe | Provincia | PK | Línea | A la vía | Motivo |
|---|---|---|---|---|---|
| `ES-ES 18.11.2014 151124-141118-IF-CIAF` | Tarragona | PK 0+571 | Línea 622 Aguja Clasif. PK | 0 m | cae sobre OTRA vía: a 0 m del tramo 022100150 (línea 210), la declarada 622 está a 2404 m |
| `ES-ES 25.01.2016 170331-160125-IF-CIAF` | Alicante | 435,900 | 336 El Reguerón a Alacant  | 0 m | cae sobre OTRA vía: a 0 m del tramo 033300025 (línea 330), la declarada 336 está a 12898 m |
| `ES-IF-060910-290711-CIAF` | Badajoz | 24+420 | 510 Aljucén - Cáceres | 0 m | cae sobre OTRA vía: a 0 m del tramo 045160010 (línea 516), la declarada 510 está a 22517 m |
| `ES-IF-240608-281108-CIAF` | Barcelona | 26,100 | 276 Barcelona Sagrera a Ma | 0 m | cae sobre OTRA vía: a 0 m del tramo 022220010 (línea 222), la declarada 276 está a 12606 m |


**DUDOSOS: ninguno.**


## 6. Cache-busting del frontend

- **[OK]** VERSION_DATOS: 2026-09-27-3 cubre la DB (2026-09-27)
