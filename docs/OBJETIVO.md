# Objetivo y criterios de aceptación — corpus ERA en castellano

> Contrato de trabajo acordado con David el 2026-11-19. «Terminado» significa TODO esto
> en verde, medido con `scripts/informe.py` (que lee del disco, no de la memoria).

## Objetivo

Pasar a castellano **todos** los informes de investigación de accidentes ferroviarios
publicados por ERA (28 países, 4.015 PDF), con calidad verificada y auditada, organizados
por país y año en `md-es/<CC>/<AAAA>/<slug>.md`.

## Criterios de aceptación

| # | Criterio | Cómo se comprueba |
|---|---|---|
| 1 | **Cobertura**: un md-es por cada md extraído (3.963) | `informe.py`: columna MD-es == columna MD en todos los países |
| 2 | **Cero vacías**: ninguna traducción por debajo del 30 % del original | `traducir_md_es.py --vacios` → 0 en todos los países |
| 3 | **Verificación**: sin páginas con pérdida de cifras | `verificacion: revisar` solo donde el revisor IA lo confirme como real |
| 4 | **Revisión IA ≥ 10 %** del corpus (≥ 397 informes) con 6 páginas cada uno | `data/revision/*.json`: suma de informes revisados |
| 5 | **Calidad por país**: ningún país con fidelidad media < 90 | `informe.py`: columna Fidelidad |
| 6 | **País con baja calidad → corregido**: si media < 92, se repara página a página y se vuelve a revisar | bitácora `data/maraton.log` |
| 7 | **Custodia**: cada md-es con `md_origen`, `md5_origen`, `modelo`, `veredicto`; cada OCR con motor, idiomas y confianza | frontmatter + `data/ocr/<CC>.json` |
| 8 | **Informe final** en `INFORME.md` con la tabla de los 28 países y el método | `scripts/informe.py` |

## Reglas de ejecución

- Concurrencia: **5 llamadas de día, 6 de 00:00 a 06:00** (medido: ~60 k caracteres/min).
  Traducción y revisión nunca a la vez.
- **Reparación por página**, no por informe: `--reparar` re-traduce solo lo que falla.
- **Nunca se maquilla**: lo que no se puede medir se declara (`sin_texto`, `sin_dictamen`).
- Los PDF escaneados (169) entran por OCR auditado; si la confianza < 70, revisión manual.