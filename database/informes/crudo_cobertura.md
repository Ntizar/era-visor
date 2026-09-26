# Cobertura de la Fase 2 (crudo)

- md procesados: **372**
- escritos ahora: 372 · saltados: 0 · fallos: 0

| Métrica | Valor |
|---|---|
| campos con valor | 15767 / 26040 (60.5%) |
| **deterministas con cita literal** | 2520/2520 (**100.0%** — gate: 100%) |
| con cita literal (cualquier origen) | 9306/15767 (59.0%) |
| **con trazabilidad (cita o procedencia)** | 15767/15767 (**100.0%** — gate: 95%) |

> `cita` = valor impreso en el md (página + texto literal).
> `procedencia` = valor derivado por el pipeline LLM anterior (v3.*):
> trazable al informe, pero NO es cita literal y por eso no se
> marca como verificado.

## Cobertura por campo

| Ref | Campo | con valor | con evidencia | verificados | estado |
|---|---|---|---|---|---|
| 0.1 | Número de referencia del informe | 369/372 | 369/372 | 369/372 | OK |
| 1.3 | Consecuencias principales | 351/372 | 138/372 | 138/372 | OK |
| 2.1.1 | Tipo de suceso | 351/372 | 185/372 | 185/372 | OK |
| 2.1.10 | Consecuencias inicialmente identificadas | 351/372 | 138/372 | 138/372 | OK |
| 2.1.6 | Descripción de los hechos | 351/372 | 87/372 | 87/372 | OK |
| 2.2.1.A | Personal ferroviario implicado | 351/372 | 249/372 | 249/372 | OK |
| 2.2.2 | Trenes implicados y composición | 351/372 | 350/372 | 350/372 | OK |
| 2.2.5 | Descripción de la infraestructura: vía, agujas y otros e | 351/372 | 241/372 | 241/372 | OK |
| 2.3.3 | Material rodante | 351/372 | 59/372 | 59/372 | OK |
| 2.3.4 | Infraestructura | 351/372 | 241/372 | 241/372 | OK |
| 1.1 | Descripción breve del suceso | 349/372 | 4/372 | 4/372 | OK |
| 1.2 | Fecha, hora y lugar del suceso | 349/372 | 349/372 | 248/372 | OK |
| 1.4 | Causas directas | 349/372 | 89/372 | 89/372 | OK |
| 2.1.2 | Administrador de infraestructura y empresas ferroviarias | 349/372 | 348/372 | 348/372 | OK |
| 2.1.3.A | Fecha | 349/372 | 308/372 | 308/372 | OK |
| 2.1.3.C | Localización exacta del suceso | 349/372 | 349/372 | 349/372 | OK |
| 2.1.5 | Identificación y características de los vehículos ferrov | 349/372 | 57/372 | 57/372 | OK |
| 2.1.7 | Descripción del lugar del accidente/incidente | 349/372 | 349/372 | 349/372 | OK |
| 2.2.3 | Matrícula del material rodante implicado | 349/372 | 57/372 | 57/372 | OK |
| 2.3.1.A | Viajeros | 349/372 | 160/372 | 160/372 | OK |
| 2.3.1.B | Personal ferroviario | 349/372 | 252/372 | 252/372 | OK |
| 2.3.1.C | Terceras personas | 349/372 | 125/372 | 125/372 | OK |
| 3.4.3 | Infraestructura | 349/372 | 239/372 | 239/372 | OK |
| 3.4.5 | Material rodante | 349/372 | 57/372 | 57/372 | OK |
| 4.1 | Descripción definitiva de la cadena de acontecimientos | 349/372 | 85/372 | 85/372 | OK |
| 4.3.1 | Causas directas e inmediatas del suceso | 349/372 | 89/372 | 89/372 | OK |
| 4.3.2 | Factores coadyuvantes | 349/372 | 58/372 | 58/372 | OK |
| 3.6.1 | Accidente con precursor o causa Factor Humano | 348/372 | 55/372 | 55/372 | OK |
| 2.4.2 | Referencias geográficas | 347/372 | 346/372 | 0/372 | OK |
| 1.7 | Recomendaciones principales | 346/372 | 319/372 | 319/372 | OK |
| 4.6.1 | Recomendaciones de seguridad | 345/372 | 318/372 | 318/372 | OK |
| 2.2.6 | Sistema de señalización, enclavamiento, señales y protec | 340/372 | 67/372 | 67/372 | OK |
| 3.4.1 | Sistema de control de mando y señalización | 340/372 | 67/372 | 67/372 | OK |
| 2.1.4 | Identificación y características de la infraestructura f | 335/372 | 295/372 | 295/372 | OK |
| 1.5 | Factores coadyuvantes | 322/372 | 54/372 | 54/372 | OK |
| 2.1.3.B | Hora | 310/372 | 271/372 | 271/372 | OK |
| 1.8 | Destinatarios de las recomendaciones | 309/372 | 282/372 | 282/372 | OK |
| 2.4.1 | Condiciones meteorológicas | 301/372 | 58/372 | 58/372 | OK |
| 2.4.3 | Condiciones de visibilidad, iluminación u otras condicio | 298/372 | 57/372 | 57/372 | OK |
| 2.2.4 | Subsistema afectado | 253/372 | 190/372 | 190/372 | OK |
| 1.6 | Causas subyacentes | 241/372 | 24/372 | 24/372 | OK |
| 4.2 | Análisis de los hechos y eficacia de los servicios de sa | 199/372 | 199/372 | 199/372 | OK |
| 3.4.4 | Equipo de comunicaciones | 177/372 | 177/372 | 177/372 | OK |
| 4.6.2.A | Destinatarios de las recomendaciones | 172/372 | 172/372 | 172/372 | OK |
| 2.2.7 | Sistemas de comunicación | 162/372 | 162/372 | 162/372 | OK |
| 3.6.2 | Tiempo de trabajo del personal implicado | 162/372 | 162/372 | 162/372 | OK |
| 4.3.4 | Causas relacionadas con el marco normativo | 134/372 | 134/372 | 134/372 | OK |
| 4.3.3 | Causas subyacentes relacionadas con cualificaciones del  | 131/372 | 131/372 | 131/372 | OK |
| 2.1.11 | Medidas inmediatas adoptadas por la entidad | 98/372 | 98/372 | 98/372 | OK |
| 4.5.2 | Medidas adoptadas después del análisis | 98/372 | 98/372 | 98/372 | OK |
| 4.5.3 | Medidas preventivas para evitar la repetición del suceso | 98/372 | 98/372 | 98/372 | OK |
| 4.5.1 | Medidas adoptadas inmediatamente | 81/372 | 81/372 | 81/372 | OK |
| 3.7.1 | Otros sucesos anteriores de carácter similar | 71/372 | 71/372 | 71/372 | OK |
| 4.6.3 | Implementadores previstos | 63/372 | 63/372 | 63/372 | OK |
| 3.6.6 | Factores humanos y organizativos relevantes | 49/372 | 49/372 | 49/372 | OK |
| 3.5.1 | Medidas tomadas por el personal de circulación | 42/372 | 42/372 | 42/372 | OK |
| 2.2.1.B | Terceros implicados | 35/372 | 35/372 | 35/372 | OK |
| 2.2.9 | Obras en el lugar o en sus cercanías | 35/372 | 35/372 | 35/372 | OK |
| 3.6.5 | Diseño del equipo con efectos en la interfaz hombre-máqu | 34/372 | 34/372 | 34/372 | OK |
| 4.4 | Observaciones adicionales | 26/372 | 26/372 | 26/372 | OK |
| 3.6.3 | Circunstancias médicas y personales con posible influenc | 2/372 | 2/372 | 2/372 | OK |
| 2.3.2 | Carga | 1/372 | 1/372 | 1/372 | OK |
| 2.3.5 | Medio ambiente | 1/372 | 1/372 | 1/372 | OK |
| 0.2 | Código interno del suceso | 0/372 | 0/372 | 0/372 | pendiente |
| 0.5 | Fecha del informe | 0/372 | 0/372 | 0/372 | pendiente |
| 0.6 | Versión / revisión del informe | 0/372 | 0/372 | 0/372 | pendiente |
| 2.1.9 | Causas presuntas inicialmente identificadas | 0/372 | 0/372 | 0/372 | pendiente |
| 2.3.6 | Impacto económico | 0/372 | 0/372 | 0/372 | pendiente |
| 3.6.4 | Existencia de tensión física o psicológica | 0/372 | 0/372 | 0/372 | pendiente |
| 3.7.3 | Información sobre riesgos, defectos o disconformidades c | 0/372 | 0/372 | 0/372 | pendiente |
