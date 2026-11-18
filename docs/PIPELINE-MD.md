# Pipeline MD — de PDF oficial a base de datos en castellano

> Norma del proyecto. Una sola fuente: si algo cambia aquí, cambia el script y el script
> manda. Los números de estado viven en `ESTADO.md` (generado), no en este documento.

## Idea

Los informes oficiales de investigación de accidentes ferroviarios están en PDF, en 28
idiomas, con maquetas distintas cada país. El objetivo es convertirlos en **una colección
Markdown en castellano, normalizada y verificada**, organizada por país y año, que sea la
base de la base de datos.

```
ERA (era.europa.eu)
   └─ /era-folder/<pais>-investigations/<año>  →  data/pdf-manifest/<CC>.json   [scrape_pais.py]
        └─ pdfs/<CC>/*.pdf                     →  fuera de git (pesado, reproducible)  [descargar_pdfs.py]
             └─ md/<CC>/<AAAA>/<slug>.md       →  original, extracción tipográfica v3  [convertir_md_pais.py]
                  └─ md-es/<CC>/<AAAA>/<slug>.md → castellano normalizado           [traducir_md_es.py]
                       └─ data/revision/<CC>.json → revisión IA contra el original   [revisar_md_es.py]
```

## Etapas y garantías

| Etapa | Script | Garantía que se verifica |
|---|---|---|
| 1. Manifiesto | `scrape_pais.py` | Un registro por PDF publicado, con año y URL oficial. Reintentos con espera (ERA limita a 429). |
| 2. Descarga | `descargar_pdfs.py`, `descargar_todo.py` | Reanudable; ningún PDF entra al pipeline sin estar completo en disco. |
| 3. Extracción | `convertir_md_pais.py` | **Cero invención**: cada línea emitida debe ser substring del texto del PDF (`verbatim_fallos` en el frontmatter). Encabezados por tamaño de fuente, no por regex. Membrete repetido eliminado. Tablas reales → pipes. Si una página no tiene capa de texto, se marca `escaneado: true` y queda vacía: nunca se rellena a mano. |
| 4. Traducción | `traducir_md_es.py` | Castellano de España, fidelidad literal, tablas celda a celda, secciones canónicas. Cada bloque se **verifica**: marcadores `## Página N` idénticos, tokens numéricos coincidentes (tolerancia 2 %), ratio de longitud 0,75-1,60. Si falla, un reintento correctivo; si sigue fallando, `verificacion: revisar` con el motivo escrito. |
| 5. Revisión IA | `revisar_md_es.py` | Modelo distinto del traductor (deepseek) compara original vs castellano página a página y devuelve fidelidad 0-100, omisiones, invenciones y números. Umbral 85. |
| 6. Estado | `estado_paises.py` | `ESTADO.md` + `md-es/<CC>/INDICE.md` generados del disco, nunca a mano. |

## Reglas que no se negocian

1. **Original y traducción no se mezclan.** `md/` es lo que dice el PDF en su idioma;
   `md-es/` es la traducción. Cualquier duda se resuelve contra `md/` y, en última
   instancia, contra el PDF (URL oficial en el frontmatter).
2. **Nada se rellena a mano.** Ni un dato, ni una frase. Si el PDF no lo dice, no está.
   Los huecos se marcan (`escaneado`, `verificacion: revisar`), no se tapan.
3. **Cada fichero lleva su cadena de custodia** en el frontmatter: `pdf`, `md5_pdf`,
   `url_oficial`, `paginas`, `chars`, fecha y generador.
4. **El modelo se anota siempre.** `modelo:` en cada md-es. Cambiar de modelo no puede
   ser invisible: la revisión se repite si cambia el traductor.
5. **Los PDFs no van al repo** (`pdfs/` está en `.gitignore`): son reproducibles desde el
   manifiesto y pesan gigas. Los `.md` sí van, versionados por país y año.

## Coste y ritmo

- Traducción en lote con `qwen3.8-flash` **con `enable_thinking: false`** (sin eso el modelo
  se come el presupuesto en razonamiento, tarda 12× más y devuelve vacío).
- Revisión con `deepseek-v4-pro` y **máximo 3 hilos/sesiones** a la vez.
- Todo es reanudable: `data/traduccion/<CC>.json` y `data/revision/<CC>.json` guardan el
  estado informe a informe. Volver a lanzar un país sólo hace lo que falta.

## Orden de fases

Se sube país a país, de los pequeños a los grandes (LU, CH, EE, SI, LT, LV, IE → PT, BE,
NL, AT, DK, FI, SE → FR, IT, PL, UK, DE → CZ, HU, RO), porque cada país pequeño es una
prueba completa del pipeline antes de escalar. España ya está hecha (351 informes CIAF/ERA).
