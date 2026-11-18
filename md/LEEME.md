# `md/` — extracción original, por país y año

Aquí está el texto de cada PDF oficial **tal y como lo dice el PDF**, en su idioma
(`idioma:` en el frontmatter de cada fichero). La traducción al castellano vive en
`md-es/`, en la misma estructura de país/año y con el mismo nombre de fichero.

```
md/<CC>/<AAAA>/<slug>.md
```

- `<CC>` — código de país de ERA (AT, BE, BG, CH, CZ, DE, DK, EE, EL, ES, FI, FR, HR,
  HU, IE, IT, LT, LU, LV, NL, NO, PL, PT, RO, RS, SE, SI, SK, UK).
- `<AAAA>` — año del informe según `data/pdf-manifest/<CC>.json` (`sin-ano` si ERA no lo
  declara).
- `<slug>` — nombre original del PDF, sin entidad HTML y sin caracteres prohibidos.

Cada fichero lleva su cadena de custodia en el frontmatter: `pdf`, `md5_pdf`, `url_oficial`,
`paginas`, `chars`, `tablas`, `verbatim_fallos`, `escaneado`, `paginas_sin_texto`,
`fecha_proceso` y `generador`.

Reglas que no se rompen:

1. **Cero invención.** `verbatim_fallos` cuenta las líneas que no se han podido verificar
   contra el texto del PDF; si no es 0, el fichero está mal y se regenera.
2. **Nada se rellena a mano.** Una página sin capa de texto queda vacía y se declara
   (`paginas_sin_texto`). No se inventa contenido que el PDF no tiene.
3. **Original y traducción no se mezclan.** Para dudar de `md-es/`, se mira aquí; para
   dudar de aquí, se abre el PDF con `url_oficial`.

Norma del pipeline: [`docs/PIPELINE-MD.md`](../docs/PIPELINE-MD.md).
Estado real por país: [`ESTADO.md`](../ESTADO.md).
