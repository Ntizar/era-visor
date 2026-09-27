# SPEC — Visor nueva pantalla (frontend/index.html)

> Contrato. Ejecuta TODO lo de aquí. Prioridad sobre esta spec: lo que veas en el repo.
> Al final, ejecuta la VERIFICACIÓN y pega la salida real.

Repo: `C:\Users\d_ant\Projects\era-visor`. Único fichero a tocar: **`frontend/index.html`**
(SPA de ~1.225 líneas: HTML + CSS + JS inline). NO toques ningún otro fichero.

## 1. Contrato de datos (ya generado por `scripts/consolidar.py ES`)

Carga en tres tiempos — esto es el alma del cambio:

| Cuándo | Fichero | Uso | Peso |
|---|---|---|---|
| Arranque | `data/db/index.json` | **tabla, mapa, filtros y KPIs** — se pinta sin esperar nada más | ~380 KB |
| 1ª vez que se abre la pestaña Dashboard | `data/db/dashboard.json` | solo campos de gráficos: `{id: {causa_directa, causas{directa,contribuyentes,sistemicas}, precursores[], factores_humanos[], mitigaciones[], meteorologia[], circulation_type, fase_ciclo_vida, velocidad_maxima, clima, tags[]}}` | ~600 KB, se cachea en memoria |
| Al abrir la ficha de un informe | `data/db/detalle/<id>.json` | registro COMPLETO (con `v3`, `trenes`, `entidades`, `recomendaciones`, `cronologia`, `hechos`, `conclusiones`…) | ~12 KB |

**Elimina** cualquier petición a `data/db/reports/ES.json` (4,4 MB). Añade `?v=VERSION_DATOS`
a las peticiones nuevas como ya se hace con las actuales.

### Campos de `index.json` (uno por informe)
`id, pais, clave, expediente, fecha, anio, hora, titulo, titulo_normalizado, tipo, tipo_categoria,
tipo_informe, gravedad, fallecidos, heridos_graves, heridos_leves, estacion, provincia, pk, linea,
lat, lng, metodo_geo, geo_veredicto, geo_dist_m, fuente, url_pdf, subsistema, sistema_proteccion,
tipo_red, explotacion, entidades[], n_recomendaciones, n_cronologia, n_trenes, n_documentos,
victimas_total`

### Campos del registro completo (`detalle/<id>.json`)
Además de los anteriores: `ubicacion_nombre, causa_directa, resumen, hechos, conclusiones,
precursores[], mitigaciones[], factores_humanos[], meteorologia[], recomendaciones[],
cronologia[], trenes[], danos_materiales, documentacion, fuentes[], id_sha1, fecha_consulta,
y todo `v3`: {titulo_normalizado, lugar, clima, hechos, cronologia[], infraestructura{...},
personal, trenes, material_rodante, causas{directa,contribuyentes,sistemicas}, consecuencias,
lecciones[], recomendaciones[{numero,destinatario,implementador,texto,pagina}], tags[]}.

## 2. Qué se conserva SIN TOCAR la lógica (ya funciona y es buena)

- Mapa Leaflet 1.9.4 + markercluster con capas **IGN WMTS** (gris/topo/orto) y **WMS ADIF**;
  `pintaMapa`, `colorPunto`, popups.
- Los filtros del `#sidebar` y `aplicaFiltros()` (país, tipo, año, víctimas, informe, geo,
  subsistema, ATP, red, entidad, explotación, búsquedas).
- Los gráficos Chart.js existentes y sus `CAUSA_BUCKETS` / `FACTOR_BUCKETS` / `TIPO_A_CATEGORIA`.
- Export a Excel con SheetJS (`XLSX`).
- Los tres tabs (`data-tab="mapa|dashboard|informes"`), `#detailPanel`, `#loadingOverlay`, footer.

## 3. Cambios exigidos

### 3.1 Carga (que cargue mejor)
- Arranque: pedir SOLO `index.json` → pintar mapa + tabla + KPIs lo antes posible
  (el overlay de carga desaparece al tener el índice, no después de todo).
- `dashboard.json`: pedirlo **la primera vez que se pulsa la pestaña Dashboard** y memorizarlo
  (`let DASH = null`); mientras no llegue, mostrar un spinner discreto en la zona de gráficos.
- Ficha: `detalle/<id>.json` bajo demanda con `encodeURIComponent(id)`; **memoriza** los
  ya pedidos (`Map` de caché) para no repetir; mientras llega, la ficha se abre ya con lo del
  índice (clave, fecha, título, víctimas) y el resto se rellena.
- Errores de red: mensaje discreto + reintento, nunca pantalla en blanco.

### 3.2 Dashboard (mucho mejor)
- **KPIs** (7 actuales) + añade: `Recomendaciones` (suma de `n_recomendaciones`), `Informes con
  fallecidos`, `Provincias distintas`, `% geolocalizado`. Cada KPI con su variación sobre el
  periodo anterior si procede; sin adornos.
- Conserva todos los charts actuales pero ahora tirando de `DASH` (campos de la tabla de arriba)
  en lugar de `r.v3.*`; los que necesiten `v3` (velocidad, causas) usan `DASH`.
- **Charts nuevos**: (a) recomendaciones por destinatario (top 8, desde el `dashboard.json` NO
  existe → si no hay dato en el índice, omite este chart y dilo), (b) distribución de
  `n_documentos` (informes con doble documento), (c) evolución de fallecidos vs sucesos
  en la misma gráfica ya existente si es fácil.
- Borrar/bloquear charts sin datos (ya hace `opacity .45`) — que nunca se vea una gráfica vacía.

### 3.3 Tabla (mucha más información)
Columnas visibles (en este orden), con ordenación al pulsar la cabecera y guardado del orden:
`clave | fecha | IF (título) | tipo/categoría | provincia | estación | línea | pk |
fallecidos | her. graves | her. leves | víct. total | recomend. (n) | geo | PDF`

- Cabecera fija, filas de 44 px, clic en la fila abre la ficha.
- En móvil (<768px) la tabla pasa a **tarjetas apiladas** (misma información, sin scroll horizontal).
- Búsqueda en la tabla + contador (`resultCount`) conservados.
- `n_recomendaciones` como badge neutro; si es 0, guion.
- `geo`: ✓ ok / ? duda / ✕ mal / — sin coords (con `title` del `geo_motivo` y `metodo_geo`).
- Seleccionables las columnas: un `select` discreto "Columnas" que muestre/oculte.

### 3.4 Ficha completa (al abrir un informe)
Cabecera: `clave` (IF NNNN/AAAA), fecha + hora, título descriptivo, badges de víctimas,
tipo/categoría, enlace **PDF ↗** (si hay `url_pdf`) y a la fuente (`fuente`/ERA).

Cuerpo en secciones (solo las que tengan contenido; todo en castellano):
1. **Datos** — clave, expediente, año, tipo de informe (`tipo_informe`), nº de documentos,
   páginas, provincia, estación, ubicación, línea, PK, entidad(es), explotación, subsistema,
   ATP, tipo de red, velocidad máxima, coordenadas + método + veredicto (si `geo_veredicto`
   ≠ 'bien', aviso), fecha de consulta.
2. **Resumen** (`resumen`).
3. **Hechos** (`hechos`) — si es muy largo, plegable con "Ver más" (no cortes la información).
4. **Cronología** (`cronologia`: lista de `{fecha, hora, texto}`) como línea de tiempo vertical.
5. **Consecuencias** (`v3.consecuencias`, `fallecidos`, `heridos_*`, `danos_materiales`).
6. **Causas** — `v3.causas.directa`, `contribuyentes[]`, `sistemicas[]` + `causa_directa`.
7. **Factores humanos / precursores / mitigaciones / meteorología** (chips).
8. **Infraestructura** (`v3.infraestructura`), **Personal** (`v3.personal`),
   **Trenes** (`trenes` o `v3.trenes`), **Material rodante** (`v3.material_rodante`) en
   tablas o listas de pares etiqueta/valor (nada de párrafos pegados).
9. **Recomendaciones** — TABLA con columnas `Nº | Destinatario | Implementador | Texto | Página`.
   Si solo vienen texto libre, filas con nº y texto. Esto es lo que permite filtrar por tipo
   en la base; en la ficha se muestra entero.
10. **Lecciones aprendidas** (`v3.lecciones`) y **Conclusiones** (`conclusiones`).
11. **Documentos** — cada entrada de `documentos`/`fuentes` con su enlace.

Al pie del panel: `id` técnico, `id_sha1`, enlace al informe original.

### 3.5 Estilo (normas duras del dueño del repo)
- **Un solo azul `#2563eb`** (acentos, enlaces, focos, botón activo). Rojo `#dc2626` SOLO
  para fallecidos/errores; ámbar `#d97706` solo para heridos graves/avisos.
- **Sobre blanco sólido**. SIN gradientes, SIN glass/blur, SIN skins, SIN sombras recargadas.
- Tipografía heredada del sistema; números tabulares donde cuadre.
- **Mobile-first y táctil: todo clic 44×44 px mínimo.**
- Nada de «AI slop»: el color solo marca datos, un número entero solo si es un dato.
- Rendimiento: sin librerías nuevas; respeta los CDN actuales (no añadas más).

## VERIFICACIÓN (obligatoria, pega la salida real)

Ejecuta un script propio (Python) que compruebe el fichero escrito:
- [ ] No queda ninguna referencia a `reports/ES.json`.
- [ ] Existen `data/db/index.json`, `data/db/dashboard.json`, `data/db/detalle/`.
- [ ] Todos los `getElementById('x')`/`querySelector('#x')` usados en JS tienen su elemento
      `<... id="x">` en el HTML (lista los que falten: debe ser 0).
- [ ] No hay `undefined` en plantillas literales obvias: comprueba con un parser simple de
      llaves equilibradas y sintaxis JS básica (puedes usar `node --check` extrayendo el `<script>`
      a un fichero temporal si node está disponible).
- [ ] `grep -c "encodeURIComponent" ≥ 1` para la ficha.
- [ ] El HTML declara viewport y tiene CSS de `@media (max-width: 768px)`.

## REGLAS
- NO hagas git commit/push. NO toques nada fuera de `frontend/index.html`.
- Castellano en TODO (textos de UI, comentarios, títulos de columna).
- Si no puedes verificar algo, dilo explícitamente en el resumen final en vez de afirmarlo.
- Resumen final: qué has cambiado, resultados de la verificación y dudas abiertas.
