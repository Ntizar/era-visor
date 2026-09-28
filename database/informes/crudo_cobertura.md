# Cobertura de la Fase 2 (crudo)

- md procesados: **351**
- escritos ahora: 1 · saltados: 0 · fallos: 0

| Métrica | Valor |
|---|---|
| campos con valor | 15674 / 24570 (63.8%) |
| **deterministas con cita literal** | 2427/2427 (**100.0%** — gate: 100%) |
| con cita literal (cualquier origen) | 9213/15674 (58.8%) |
| **con trazabilidad (cita o procedencia)** | 15674/15674 (**100.0%** — gate: 95%) |

> `cita` = valor impreso en el md (página + texto literal).
> `procedencia` = valor derivado por el pipeline LLM anterior (v3.*):
> trazable al informe, pero NO es cita literal y por eso no se
> marca como verificado.

## Cobertura por campo

| Ref | Campo | con valor | con evidencia | verificados | estado |
|---|---|---|---|---|---|
| 0.1 | Número de referencia del informe | 350/351 | 350/351 | 350/351 | OK |
| 1.1 | Descripción breve del suceso | 349/351 | 4/351 | 4/351 | OK |
| 1.2 | Fecha, hora y lugar del suceso | 349/351 | 349/351 | 248/351 | OK |
| 1.3 | Consecuencias principales | 349/351 | 136/351 | 136/351 | OK |
| 1.4 | Causas directas | 349/351 | 89/351 | 89/351 | OK |
| 2.1.1 | Tipo de suceso | 349/351 | 183/351 | 183/351 | OK |
| 2.1.10 | Consecuencias inicialmente identificadas | 349/351 | 136/351 | 136/351 | OK |
| 2.1.2 | Administrador de infraestructura y empresas ferroviarias | 349/351 | 348/351 | 348/351 | OK |
| 2.1.3.A | Fecha | 349/351 | 308/351 | 308/351 | OK |
| 2.1.3.C | Localización exacta del suceso | 349/351 | 349/351 | 349/351 | OK |
| 2.1.5 | Identificación y características de los vehículos ferrov | 349/351 | 57/351 | 57/351 | OK |
| 2.1.6 | Descripción de los hechos | 349/351 | 85/351 | 85/351 | OK |
| 2.1.7 | Descripción del lugar del accidente/incidente | 349/351 | 349/351 | 349/351 | OK |
| 2.2.1.A | Personal ferroviario implicado | 349/351 | 247/351 | 247/351 | OK |
| 2.2.2 | Trenes implicados y composición | 349/351 | 348/351 | 348/351 | OK |
| 2.2.3 | Matrícula del material rodante implicado | 349/351 | 57/351 | 57/351 | OK |
| 2.2.5 | Descripción de la infraestructura: vía, agujas y otros e | 349/351 | 239/351 | 239/351 | OK |
| 2.3.1.A | Viajeros | 349/351 | 160/351 | 160/351 | OK |
| 2.3.1.B | Personal ferroviario | 349/351 | 252/351 | 252/351 | OK |
| 2.3.1.C | Terceras personas | 349/351 | 125/351 | 125/351 | OK |
| 2.3.3 | Material rodante | 349/351 | 57/351 | 57/351 | OK |
| 2.3.4 | Infraestructura | 349/351 | 239/351 | 239/351 | OK |
| 3.4.3 | Infraestructura | 349/351 | 239/351 | 239/351 | OK |
| 3.4.5 | Material rodante | 349/351 | 57/351 | 57/351 | OK |
| 4.1 | Descripción definitiva de la cadena de acontecimientos | 349/351 | 85/351 | 85/351 | OK |
| 4.3.1 | Causas directas e inmediatas del suceso | 349/351 | 89/351 | 89/351 | OK |
| 4.3.2 | Factores coadyuvantes | 349/351 | 58/351 | 58/351 | OK |
| 3.6.1 | Accidente con precursor o causa Factor Humano | 348/351 | 55/351 | 55/351 | OK |
| 2.4.2 | Referencias geográficas | 347/351 | 346/351 | 0/351 | OK |
| 2.2.6 | Sistema de señalización, enclavamiento, señales y protec | 340/351 | 67/351 | 67/351 | OK |
| 3.4.1 | Sistema de control de mando y señalización | 340/351 | 67/351 | 67/351 | OK |
| 1.7 | Recomendaciones principales | 334/351 | 307/351 | 307/351 | OK |
| 2.1.4 | Identificación y características de la infraestructura f | 333/351 | 293/351 | 293/351 | OK |
| 4.6.1 | Recomendaciones de seguridad | 333/351 | 306/351 | 306/351 | OK |
| 1.5 | Factores coadyuvantes | 322/351 | 54/351 | 54/351 | OK |
| 2.1.3.B | Hora | 310/351 | 271/351 | 271/351 | OK |
| 2.4.1 | Condiciones meteorológicas | 301/351 | 58/351 | 58/351 | OK |
| 2.4.3 | Condiciones de visibilidad, iluminación u otras condicio | 298/351 | 57/351 | 57/351 | OK |
| 1.8 | Destinatarios de las recomendaciones | 297/351 | 270/351 | 270/351 | OK |
| 2.2.4 | Subsistema afectado | 253/351 | 190/351 | 190/351 | OK |
| 1.6 | Causas subyacentes | 241/351 | 24/351 | 24/351 | OK |
| 4.2 | Análisis de los hechos y eficacia de los servicios de sa | 199/351 | 199/351 | 199/351 | OK |
| 3.4.4 | Equipo de comunicaciones | 175/351 | 175/351 | 175/351 | OK |
| 2.2.7 | Sistemas de comunicación | 160/351 | 160/351 | 160/351 | OK |
| 3.6.2 | Tiempo de trabajo del personal implicado | 160/351 | 160/351 | 160/351 | OK |
| 4.6.2.A | Destinatarios de las recomendaciones | 160/351 | 160/351 | 160/351 | OK |
| 4.3.4 | Causas relacionadas con el marco normativo | 134/351 | 134/351 | 134/351 | OK |
| 4.3.3 | Causas subyacentes relacionadas con cualificaciones del  | 131/351 | 131/351 | 131/351 | OK |
| 2.1.11 | Medidas inmediatas adoptadas por la entidad | 98/351 | 98/351 | 98/351 | OK |
| 4.5.2 | Medidas adoptadas después del análisis | 98/351 | 98/351 | 98/351 | OK |
| 4.5.3 | Medidas preventivas para evitar la repetición del suceso | 98/351 | 98/351 | 98/351 | OK |
| 4.5.1 | Medidas adoptadas inmediatamente | 81/351 | 81/351 | 81/351 | OK |
| 3.7.1 | Otros sucesos anteriores de carácter similar | 71/351 | 71/351 | 71/351 | OK |
| 4.6.3 | Implementadores previstos | 63/351 | 63/351 | 63/351 | OK |
| 3.6.6 | Factores humanos y organizativos relevantes | 49/351 | 49/351 | 49/351 | OK |
| 3.5.1 | Medidas tomadas por el personal de circulación | 42/351 | 42/351 | 42/351 | OK |
| 2.2.1.B | Terceros implicados | 35/351 | 35/351 | 35/351 | OK |
| 2.2.9 | Obras en el lugar o en sus cercanías | 35/351 | 35/351 | 35/351 | OK |
| 3.6.5 | Diseño del equipo con efectos en la interfaz hombre-máqu | 34/351 | 34/351 | 34/351 | OK |
| 4.4 | Observaciones adicionales | 26/351 | 26/351 | 26/351 | OK |
| 3.6.3 | Circunstancias médicas y personales con posible influenc | 2/351 | 2/351 | 2/351 | OK |
| 2.3.2 | Carga | 1/351 | 1/351 | 1/351 | OK |
| 2.3.5 | Medio ambiente | 1/351 | 1/351 | 1/351 | OK |
| 0.2 | Código interno del suceso | 0/351 | 0/351 | 0/351 | pendiente |
| 0.5 | Fecha del informe | 0/351 | 0/351 | 0/351 | pendiente |
| 0.6 | Versión / revisión del informe | 0/351 | 0/351 | 0/351 | pendiente |
| 2.1.9 | Causas presuntas inicialmente identificadas | 0/351 | 0/351 | 0/351 | pendiente |
| 2.3.6 | Impacto económico | 0/351 | 0/351 | 0/351 | pendiente |
| 3.6.4 | Existencia de tensión física o psicológica | 0/351 | 0/351 | 0/351 | pendiente |
| 3.7.3 | Información sobre riesgos, defectos o disconformidades c | 0/351 | 0/351 | 0/351 | pendiente |
