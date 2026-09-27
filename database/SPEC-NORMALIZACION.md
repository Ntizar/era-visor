# SPEC — Normalización y entregables (Fase 5)

> Contrato de trabajo. TODO lo que aquí se dice es norma; no inventes campos ni
> rutas fuera de las indicadas. Al terminar, verifica con los comprobadores
> de la sección "VERIFICACIÓN" y pega la salida real.

## Contexto

Repo: `C:\Users\d_ant\Projects\era-visor` (git, rama `main`).
- Los md crudos de los informes están en `md/ES/*.md` (372 ficheros, frontmatter YAML + `## Página N`).
- La base de datos canónica es `data/db/reports/ES.json` (lista de registros; el campo `expediente` y `clave` son `NNNN/AAAA`).
- El Excel de la base CIAF vive en `database/data/ciaf_base_v2.xlsx` (13 hojas, ver abajo).
- El Excel "crudo" (tal cual dicen los md, con cita y página) es `database/data/ciaf_base_global.xlsx`.
- El generador de Excel existente es `database/scripts/03_exportar_excel.py` (léelo antes de tocar nada; reutiliza su estilo).

## Hojas de ciaf_base_v2.xlsx (actuales)

`Informes` (372 filas × 117 col), `Recomendaciones` (939), `Entidades`, `Cronologia`,
`Trenes`, `Personal`, `Diccionario`, `Cobertura`, `Tablas`, `Mejorado` (10017 filas
largo: clave, expediente, url_oficial, ref, valor, pagina, cita, verificado, verificacion, intentos),
`Geo`, `Analisis`, `Textos`.

## TAREA 1 — `database/scripts/07_normalizar.py` (nuevo)

Lee la base y escribe `database/data/normalizado/`:
- `00-normalizado.json` → lista de dicts, **un registro por informe principal** (351):
  clave/expediente normalizados, año, título, tipo, categoría, recomendaciones…
- `01-entregable-informes.csv` y `02-entregable-recomendaciones.csv` (UTF-8 con BOM, separador `;`)
  para que se abran bien en Excel español.

### Reglas de normalización (aplicables en TODAS las hojas y columnas)

1. **Clave/expediente → `NNNN/AAAA`** (4 dígitos + 4 cifras de año) en TODAS las hojas
   y en TODAS las columnas llamadas `clave` o `expediente`:
   - `0001/08` → `0001/2008`, `17/2007` → `0017/2007`, `0002/010` → `0002/2010`,
     `0062/07` → `0062/2007`, `012/2007` → `0012/2007`.
   - Año de 2 dígitos: `<30` → 20xx, `>=30` → 19xx.
   - Un valor que no encaje con ese patrón (p. ej. `ID_230507_140907`) → lo dejas como
     `expediente_crudo` y la clave canónica se toma del registro de `data/db/reports/ES.json`
     (búscala por `id`); si tampoco existe, deja `clave` vacía y lo marcas en el informe final.
   - Conserva SIEMPRE el valor literal original en la columna `expediente_crudo` (nueva).
2. **Año → 4 cifras** (`anio`): entero, 4 dígitos. En las hojas donde no exista la columna, créala
   derivada de `clave` ya normalizada. Cero celdas vacías salvo informes sin fecha.
3. **Tipos de suceso → taxonomía única** (valores exactos, minúsculas):
   `descarrilamiento | arrollamiento | colision | paso_a_nivel | incendio | fallos_senal | otro | indeterminado`
   - Reglas (sobre texto minúsculas-sin-acentos): contiene `colision|alcance` → `colision`;
     `descarril` → `descarrilamiento`; `arrollam|atropell` → `arrollamiento`;
     `paso a nivel|cruce` → `paso_a_nivel`; `incendio|humo|fuego` → `incendio`;
     `senal|enclavam|baliza|asfa|rebase` → `fallos_senal`;
     solo dice `accidente|incidente|grave|otro` sin tipo concreto → `otro`;
     vacío o `None` → `indeterminado`.
   - **Nunca** se mezclan formas: no puede haber `incidente` junto a `incidente ferroviario`
     en la misma columna. Añade también la columna `tipo_suceso_crudo` con el valor literal.
4. **Categoría del suceso → `categoria_suceso`** (separada del tipo):
   `accidente_grave | accidente | incidente | conato | sin_categoria`
   - `accidente ferroviario grave` → `accidente_grave`; `accidente ferroviario` → `accidente`;
     `incidente` + `incidente ferroviario` + `incidente operacional` → `incidente`;
     `conato` → `conato`; resto → `sin_categoria`.
   - Fuente: redacción del informe (título/tipo crudo). Si no hay señal → `sin_categoria`.
5. **Nada de `None`**: toda celda de tipo/categoría/clave/anio lleva valor (usa
   `indeterminado`/`sin_categoria`), nunca vacío ni `None`.

## TAREA 2 — Recomendaciones filtrables (una celda = una recomendación)

- Hoja `Recomendaciones` (una recomendación por fila, ya existe): AÑADE las columnas
  `tipo_suceso`, `categoria_suceso`, `anio` tomadas del informe al que pertenecen
  (unión por `clave`), para poder filtrar por tipo de incidente.
- Hoja `Informes`: AÑADE `n_recomendaciones` (entero) y `rec_1`, `rec_2`, `rec_3`
  (texto de la 1ª, 2ª y 3ª recomendación, en celdas SEPARADAS; vacío si no hay).
- `00-normalizado.json`: `recomendaciones` = lista de objetos
  `{numero, destinatario, implementador, texto, pagina}` (si la fuente solo trae texto
  libre, `{numero: null, texto: "..."}`).
- En `Diccionario` documenta cada columna nueva en castellano.

## TAREA 3 — Carpeta de entregables `entregables/`

Tres subcarpetas, regenerables con el script nuevo `database/scripts/08_entregables.py`
(`python database/scripts/08_entregables.py` las rehace todas):

1. `entregables/01-md-puros/` — copia literal de los 372 `md/ES/*.md` (sin tocar nada).
2. `entregables/02-excel-desde-md/ciaf_desde_md.xlsx` — Excel generado SOLO desde los md
   (lo que dicen los md, con `pagina` y `cita`, sin normalizar): es la Fase 2/3 actual.
   Regenera este fichero con `03_exportar_excel.py` (o reimplementando su lógica) y cópialo aquí.
3. `entregables/03-excel-normalizado/ciaf_normalizado.xlsx` — el `07_normalizar.py` con TODAS
   las reglas anteriores.
4. `entregables/README.md` — qué contiene cada carpeta, cómo regenerarlo y la fecha de generación.

## VERIFICACIÓN (obligatoria; pega la salida)

```bash
cd C:/Users/d_ant/Projects/era-visor
python database/scripts/07_normalizar.py
python database/scripts/08_entregables.py
```

Comprueba con un script propio y **lista los resultados reales**:
- [ ] 0 celdas `None`/vacías en columnas `clave`, `expediente`, `anio`, `tipo_suceso`, `categoria_suceso` (salvo las documentadas).
- [ ] 0 valores de `clave`/`expediente` que no casen con `^\d{4}/\d{4}$`.
- [ ] `tipo_suceso` solo toma los 8 valores canónicos (imprime `Counter` de valores únicos).
- [ ] `categoria_suceso` solo los 5 valores.
- [ ] `entregables/01-md-puros/` tiene 372 ficheros.
- [ ] Los 3 Excels se abren con openpyxl y sus hojas tienen ≥ las columnas previas.
- [ ] `git status --short` solo muestra ficheros nuevos esperados (no borres nada).

## REGLAS

- **NO borres nada** del repo; solo crear/modificar.
- NO hagas `git commit` ni `git push` (lo hago yo al final).
- NO toques `frontend/`, ni `scripts/consolidar.py`, ni `scripts/verificar_todo.py`.
- Idioma: TODO en castellano (nombres de columnas, textos, README, comentarios).
- Si algo no cuadra con lo que ves en el repo, PRIORIZA lo que ves en el repo sobre esta spec
  y dilo explícitamente en tu resumen final.
- Al final, resumen breve: ficheros creados, resultados de la verificación y cualquier desviación.
