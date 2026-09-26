# Base de Datos CIAF España — SPEC

## Visión

Convertir los informes PDF del CIAF (y los de ERA) en una **base de datos canónica,
trazable y regenerable**, donde cada dato es rastreable hasta la página exacta del
informe original, con el Excel como export y el JSON como fuente de verdad.

## Decisiones de alcance (ya tomadas)

| Decisión | Respuesta |
|---|---|
| Dónde vive | `era-visor/database/` — reutiliza los 374 PDFs, 372 `.md` y la geoloc auditada (0 duda · 0 mal). No se duplica nada. |
| Fuente de verdad | **JSON canónico**. El Excel es un **export regenerable** (no hay dos verdades que divergen). |
| Cobertura | Cruce contra el listado oficial de la web del CIAF (`infofin-AAAA`) → la DB debe tener exactamente los mismos expedientes que la web. |

## Qué SÍ hace

- Fase 0: manifest maestro 1-registro-por-informe con `url_oficial` (ERA y/o CIAF) + cruce de cobertura.
- Fase 1: mejorar el `.md` **sin LLM**: tablas → markdown, quitar índice de puntos, frontmatter de procedencia.
- Fase 2: JSON crudo por informe con **página-evidencia** en cada campo.
- Fase 3: Excel con las refs de la guía CIAF Fase I, **`url_oficial` nunca vacía**.
- Fase 4: `data_mejorado` por sistema de 4 pasadas (A determinista → B LLM → C verificación → D auditoría por clase).
- Fase 5: gate de comprobación integral apto para cron.

## Qué NO hace (non-goals)

- **No** toca la geolocalización (314 bien · 0 duda · 0 mal) ni la DB `data/db/` existente.
- **No** rehace el visor actual (`frontend/`); solo expone después datos nuevos.
- **No** inventa: si el dato no está en el informe → estado explícito `no consta` / `indeterminado`.
- **No** mezcla la causa directa del RD 929/2020 con la clasificación causal/coadyuvante/sistémica del Reg. (UE) 2020/572.
- **No** modifica `ciaf-visor-ref`.

## Fuentes

| Fuente | Uso | Nota |
|---|---|---|
| `pdfs/ES/*.pdf` + `md/ES/*.md` | 374 PDFs / 372 md ya descargados (370 con `## Página`) | UA navegador obligatoria si se re-descarga de transportes.gob.es |
| Web ERA | `url_oficial` de descarga | 348/349 registros ya la traen |
| Web CIAF `infofin-AAAA` | listado maestro de cobertura | scraping con UA de navegador + Referer |
| Guía CIAF Fase I (docx) | esquema de columnas + diccionarios B1–B12 | ~60 refs, 8 bloques |
| `data/db/reports/ES.json` | campos ya verificados (v3, geo) → se **importan**, no se re-extraen | origen `importado` |

## Arquitectura

```
era-visor/
└── database/
    ├── SPEC.md
    ├── scripts/
    │   ├── 00_manifest_maestro.py     Fase 0  fuentes + cobertura
    │   ├── 01_mejorar_md.py           Fase 1  tablas→md, índice, frontmatter
    │   ├── 02_extraer_crudo.py        Fase 2  md → json crudo (0 tokens)
    │   ├── 03_exportar_excel.py       Fase 3  json → .xlsx
    │   ├── 04_enriquecer_llm.py       Fase 4B pasada LLM por bloques
    │   ├── 05_verificar_evidencia.py  Fase 4C cita literal ↔ página
    │   ├── 06_verificar_todo.py       Fase 5  gate integral (exit≠0 si ERROR)
    │   └── diccionarios/              B1–B12 + versiones
    ├── data/
    │   ├── manifest_maestro.json
    │   ├── crudo/<id>.json            1 fichero por informe (reanudable)
    │   ├── mejorado/<id>.json
    │   └── db/ciaf_es.xlsx            export siempre regenerable
    └── informes/
        ├── cobertura.md                expedientes faltantes/sobrantes vs web CIAF
        └── verificacion.md             gate de la Fase 5
```

**Regla de contexto (el eje del diseño):** el agente **nunca** lee informes enteros;
los scripts sí. El LLM solo recibe chunks con presupuesto ≤ 10k tokens por llamada.
372 × 37 KB ≈ 14 MB y un solo md llega a 421 KB: cualquier enfoque que cargue
informes completos en contexto está condenado.

### Schema del campo canónico (cumple la regla de la guía)

```json
"expediente": {
  "valor_fuente": "0038/2017",
  "valor_normalizado": "38/2017",
  "pagina": 1,
  "cita": "Investigación del incidente nº 0038/2017",
  "origen": "determinista",          // determinista | llm | importado
  "regla": "R-exp-01",
  "diccionario": "B2-RD929/2020",    // solo si normaliza
  "version_diccionario": "2026-09-26",
  "verificado": true                 // false = cita no localizada
}
```

En campos narrativos: **etiquetas auxiliares sin sustituir el texto literal**.

## Sistema de pasadas (Fase 4)

| Pasada | Qué | Coste | Sale cuando |
|---|---|---|---|
| **A** determinista | regex/heurística para todo lo que la guía marca «Sí» | **0 tokens** | cobertura ≥ 95% en su clase de campo |
| **B** LLM | solo campos «Parcial» + huecos. **1 llamada = 1 bloque de la guía × 1 informe**, fragmento recortado por índice de secciones, ≤ 10k tokens | API | 100% de informes pasados por la cola |
| **C** verificación | ¿la `cita` literal existe en la `pagina` citada del md? Si no → `verificado=false` y vuelve a la cola | script | ≥ 95% verificados |
| **D** auditoría por clase | residuos agrupados por CLASE de fallo y corregidos de golpe, nunca caso a caso | revisión | 0 clases abiertas |

**Máximo 2 reintentos por fase**; lo que quede se lista como residuo en el informe,
nunca se rellena a ojo. La pasada C es lo que uniformiza informes con formatos
distintos: si el dato no es rastreable al texto, no entra en la base.

## Gates (una fase no avanza sin la anterior en verde)

1. **H1** `manifest_maestro.json` con `url_oficial` 100% + `cobertura.md` explicando cada diferencia vs web CIAF.
2. **H2** `.md` mejorado sin pérdida (chars antes/después auditados, tablas ≥ 0, índice de puntos = 0, frontmatter presente).
3. **H3** `crudo/*.json` = 1 por informe, **100% de campos con `pagina`+`cita`**, informe de cobertura por campo.
4. **H4** Excel: 1 fila por informe, `url_oficial` 0 vacías, hojas 1-a-N enlazadas por expediente.
5. **H5** `data_mejorado` con ≥ 95% `verificado=true` y residuos listados.
6. **H6** `06_verificar_todo.py` → exit 0 (PDF↔md↔crudo↔Excel↔DB, 1 registro/expediente, dupes md5, fantasmas).

## Anti-patrones heredados (de errores ya pagados)

- Orden de escritura: normalizar **antes** de `write_text`, nunca después.
- Índice `merged = index + overlay` fantasma → reemplazar, no acumular.
- Dedupe **bidireccional** por expediente; nunca borrar, mover a `_duplicados_descartados/`.
- Un solo proceso LLM a la vez (dos estructuradores colisionan en escrituras).
- API NaN: 3 reintentos con sleep ante 524/429; JSON con `.replace('{var}')`, no `.format()`.
- Verificación = **script fija**, no lista ad hoc por sesión.
- `VERSION_DATOS` + cache-busting en todo lo que se publique.

## Criterios de éxito

- 100% de filas con enlace vivo al informe original (CIAF o ERA).
- 100% de celdas de dato con `página` + `cita` verificable.
- Regenerar el Excel completo desde cero = un comando.
- Cobertura idéntica a la web oficial del CIAF.
