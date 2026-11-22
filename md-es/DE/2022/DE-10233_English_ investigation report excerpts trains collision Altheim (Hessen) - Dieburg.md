---
pais: DE
anio: 2022
idioma_origen: EN
md_origen: md/DE/2022/DE-10233_English_ investigation report excerpts trains collision Altheim (Hessen) - Dieburg.md
md5_origen: 4cd60750b34c1f17e3308c145719ac33
modelo: mimo-v2.6-flash
bloques: 4
chars: 34939
ratio_longitud: 1.06
tokens_in: 10022
tokens_out: 9623
verificacion: ok
fecha_proceso: 2026-11-21
generador: traducir_md_es.py (traducción IA + verificación numérica)
notas_cifras: ["página 10: cifras cortas: 2/14", "página 14: cifras largas: 1/5"]
---
## Página 1

Traducción de un extracto del informe de investigación
«Colisión de tren Altheim (Hesse) – estación de Dieburg el 19/05/2022»
Estado a 11/12/2023, versión 1.0.
Nota:
De conformidad con el artículo 3 del Reglamento de Ejecución (UE) 2020/572, los puntos 1, 5 y 6 del Anexo I de un informe de investigación deberán redactarse en una segunda lengua oficial europea. Esta traducción deberá estar disponible a más tardar tres meses después de la entrega del informe.
La siguiente traducción al inglés es un extracto correspondiente del informe de investigación. La versión en lengua alemana es la auténtica.
Traducción del extracto:
1 Resumen
La primera sección contiene una descripción breve del suceso, así como información sobre las consecuencias, las causas primarias y las recomendaciones de seguridad formuladas en el caso concreto.
1.1 Descripción breve del suceso
El 19/05/2022 a las 02:52 am, el número de tren (TN) del DGS 46192, que se encontraba entre Babenhausen y Dieburg, fue sobrescrito automáticamente con el TN del DGS 42174 posterior, a raíz de una cancelación de itinerario. Como resultado, el DGS 46192 continuó su marcha hacia Darmstadt, inicialmente sin TN y, posteriormente, con el TN incorrecto del DGS 42174. El DGS 42174 permaneció de forma no detectada en el itinerario y se detuvo entre la parada de Altheim (Hesse) y la estación de Dieburg. El despachador de Dieburg restableció finalmente el bloque, que seguía ocupado por el DGS 42174 sin que esto hubiera sido detectado. Como resultado, el GAG 60101 posterior circuló por el bloque en la posición de señal y colisionó con el DGS 42174 detenido a las aproximadamente 04:04 am.
Página 1 de 14


## Página 2

### 1.2 Consecuencias
Como resultado de la colisión, el maquinista del GAG 60101 falleció y el maquinista del DGS 42174 sufrió lesiones leves. La unidad de tracción (TU) y los primeros coches del GAG 60101 que colisionó, así como el último coche del DGS 42174, sufrieron daños significativos. También se produjeron daños materiales de gran consideración en la carga de los dos trenes y en la infraestructura.
### 1.3 Causas
La colisión se debió a una cadena de sucesos que se originó en Babenhausen.
Hora
Factor
Factor
Factor
Factor
Causal
contribuyente
sistémico
sistemático
02:52 am
Avance intempestivo del número de tren y sobrescritura del TN 46192 con el TN 42174
F1
X
X
02:53 am
Borrado automático del TN 42174 del campo de bloque 36 tras la nueva entrada manual del TN en el campo de estación
F2
X
X
02:53 am
El TN original 46192 ya no consta en el campo de bloque 36
F3
X
02:56 am
Número en blanco en el campo de TN 34 borrado por el despachador de Babenhausen
F4
X
X
03:11 am
El despachador de Dieburg asume que hay una avería
F5
X
X
03:26 am
Procedimiento de conducción a la vista implementado incorrectamente (incluida la señal de entrada 30F establecida)
F6
X
X
03:31 am
Mensaje de tiempo de espera en el bloque 34 no observado
F7
X
X
03:32/03:35 am
Consulta de posición DGS 42174
F8
X
X
03:34 am
Operación de restablecimiento del contador de ejes
F9
X
03:06/03:39 am
Ninguna consulta del maquinista 46192 sobre el motivo de la parada en señal
F10
X
Tabla 1: Resumen de los factores influyentes


## Página 3

### 1.4 Recomendaciones de seguridad
Las siguientes recomendaciones de seguridad se emiten de conformidad con la sección 6 de la Eisenbahn­Unfalluntersuchungsverordnung (EUV, reglamento alemán de investigación de accidentes ferroviarios) y el artículo 26(2) de la Directiva (UE) 2016/798. Se recomienda que
x
se examine y modifique el sistema de trabajo para el procesamiento y la transmisión de mensajes de tren, de modo que su información cumpla siempre con los requisitos establecidos en el Reg. (UE) 2018/762, Anexo 2, punto 4.4.3, en particular al transitar entre procesos automatizados y manuales.
x
se examinen y mejoren los procesos de planificación, ejecución y aprobación de las funciones de los sistemas TN de conformidad con el Reg. (UE) 2018/762 Anexo II punto 5.2.1, incluida la gestión de cambios y de riesgos asociada, a fin de garantizar que el activo físico se integre de forma segura en los sistemas de trabajo.
x
a fin de garantizar la función protectora del procedimiento de trabajo «el mismo tren ha entrado en un tramo y ha vuelto a salir» de conformidad con el Reg. (UE) 2018/762 Anexo II punto 3.1.1.1, deberán determinarse los riesgos en caso de errores por parte de las personas implicadas y mejorarse el procedimiento de trabajo.
x
de conformidad con el Reg. (UE) 2018/762 Anexo II punto 3.1.1.1, deberán determinarse los riesgos en caso de discrepancias entre la posición de un tren asumida por el despachador y la posición comunicada por el maquinista, y deberán desarrollarse procedimientos de trabajo adecuados para la continuación segura de la explotación.
x
deberán desarrollarse más las condiciones técnicas para la eficacia de la acción de mando del operador de un restablecimiento del contador de ejes, a fin de minimizar aún más o excluir los riesgos de acciones de mando del operador exitosas e intempestivas. Hasta que estas medidas se implementen técnicamente, y a fin de minimizar los daños potenciales, se recomienda que se implementen soluciones compensatorias basadas en procedimientos.
## 5
### Conclusiones
La siguiente sección contiene un resumen de los factores causales, contribuyentes y sistémicos identificados. Además, se incluyen dos subsecciones adicionales con información sobre las medidas ya adoptadas y comentarios adicionales.
## 5.1
### Resumen y conclusión
La colisión se debió a una cadena de sucesos que se originó en Babenhausen. El punto de partida fue el avance y la sobrescritura automáticos de un TN sin desplazamiento del tren debido a la planificación del sistema de comunicación de TN


## Página 4

800 en Babenhausen. Varios factores causales, contribuyentes y sistémicos dieron lugar a que la cadena de sucesos continuara por parte de las personas implicadas, lo que finalmente provocó la colisión.
## 5.1.1
### Clasificación de los factores influyentes
La tabla siguiente contiene el resumen de los factores influyentes relevantes para la cadena de sucesos. Se asignan a factores causales, contribuyentes y sistémicos de conformidad con el artículo 2 del Reglamento (UE) 2020/572. Los números entre paréntesis de los factores se utilizan para facilitar su asignación a las explicaciones de los capítulos siguientes.
Aspecto parcial,
Hora
Aspecto parcial,
Aspecto parcial,
Aspecto parcial,
contribuyente
causal
sistémico
sistemático
Avance intempestivo
02:52 am
Nueva funcionalidad
del TN sin que el
implementada no
(F1) Avance intempestivo del
tren se haya
corresponde con el
número de tren y
desplazado, con
rendimiento original
sobrescritura del TN 46192 con
sobrescritura/borrado
del sistema TN
el TN 42174
de un TN normal
Información
02:53 am
borrada sin
Planificación técnica
(F2) Borrado automático del TN
conocimiento y, si
de la salida de la
42174 del campo de bloque 36
procede, cooperación
impresora para el
tras la nueva entrada manual
de los despachadores
borrado está ausente
del TN en el campo de estación
implicados
Fallo del
02:53 am
Despachador de
despachador, lo que
(F3) El TN original 46192 ya no
significa que un tren
consta en el campo de bloque 36
circulaba por el
itinerario sin TN
02:56 am
Planificación del
Reglas en la directriz
Babenhausen: acceso
sistema TN
408.0591 no
(F4) Número en blanco en el
técnico al campo de TN 34
observadas
campo de TN 34 borrado por el
era posible
despachador de Babenhausen


## Página 5

Especificaciones de
trabajo incompletas
Ninguna aclaración
en la directriz
03:11 am
sobre viajes de tren
408.0591 en relación
(F5) El despachador de Dieburg
que se han
con la información
asume que hay una avería
realizado
faltante en el sistema
TN con una
visualización
simultáneamente
ocupada
03:26 am
Error en la aplicación
Regla en la directriz
(F6) Procedimiento de conducción
de reglas resulta
408.0248 no
a la vista implementado
directamente en el
observada
incorrectamente (incluida la
fallo de sus objetivos
señal de entrada 30F establecida)
protectores
Ignorancia de avisos
03:31 am
Regla en la directriz
generados técnicamente
408.0641 no
(F7) Mensaje de tiempo de espera
debido a errores de
observada
en el bloque 34 no observado
planificación en la
infraestructura
Datos de posición
del maquinista 42174
Procedimiento para
03:32/03:35 am
no tenidos en
discrepancias en la
(F8) Consulta de posición DGS
consideración por
información de
42174
el despachador de
posición no
Dieburg
reglamentado
03:34 am
Última acción que
(F9) Operación de restablecimiento
hizo posible la
del contador de ejes para el
colisión
bloque 34
03:06/03:39 am
Reglas en la directriz
(F10) Ninguna consulta del
408.2455 no
maquinista 46192 sobre el motivo
observadas
de la parada en señal
Tabla 6: Resumen de los factores influyentes


## Página 6

El diagrama siguiente ofrece otra representación visual de los pasos clave de la cadena de sucesos en orden cronológico, separados según el gestor de infraestructura (derecha) y la empresa ferroviaria (izquierda). Los factores causales mencionados anteriormente se indican con puntos rojos, mientras que los puntos naranjas se utilizan para los factores contribuyentes.
Figura 25: Cronología de la cadena de sucesos

## Página 7

### 5.1.2 Sistemas TN
Como parte de las medidas de ajuste para el sistema de notificación TN 800 en Babenhausen, surgieron peculiaridades técnicas y operativas individuales en el enclavamiento informatizado de Dieburg, que causaron el inicio y contribuyeron a la mayor progresión de la cadena de acontecimientos.
### Factor causal
Para F1: Al cancelar una ruta de tren exterior solo preestablecida, el sistema TN de Babenhausen eliminó un mensaje de tren automatizado sin que hubiera un movimiento real de tren con aspecto de señal de vía libre y aspecto de parada. Al mismo tiempo, con esta deregistración intempestiva, el sistema TN sobrescribió un TN guardado en el bloque 36 de un tren que había salido previamente de forma correcta y había sido deregistrado automáticamente. En contraste con el Reglamento (UE) 2018/762, Anexo II, punto 4.4.3 c), la información relacionada con la seguridad generada/modificada en estas situaciones no era correcta. No correspondía a las operaciones reales. Una deregistración automatizada solo debe producirse como resultado de un viaje de tren que haya tenido lugar realmente. El sistema TN debe, por tanto, comportarse de acuerdo con los procesos permitidos para los procedimientos telefónicos de notificación de trenes, según los cuales la deregistración telefónica solo se produce si ha habido un viaje de tren real. Un TN guardado para un viaje de tren real no debería poder sobrescribirse debido a una deregistración automatizada e intempestiva. Este tipo de pérdida de datos debe evitarse.
### Factor contribuyente
Para F2: La eliminación automatizada del TN que se encontraba en el bloque 36, provocada por la nueva entrada manual, dio lugar a un cambio en los datos de las operaciones en la ruta sin que las demás personas implicadas lo supieran o fueran conscientes de ello. Antes de una eliminación manual o automatizada de un TN en la ruta, todas las personas implicadas deben ser informadas correspondientemente o dar su consentimiento basándose en un procedimiento de trabajo definido, de forma análoga a los procedimientos de notificación telefónica de trenes.
### Factores sistémicos
Para F1: El procesamiento de datos en el sistema TN, que se configuró de nueva durante el ajuste y como resultado no era correcto ni coherente, parece no haber sido identificado ni en el proceso de planificación e implementación del gestor de infraestructura, ni evaluado en términos de aceptabilidad y control suficiente mediante instrucciones de trabajo apropiadas. Los procesos del gestor de infraestructura para la planificación, implementación y puesta en servicio de comportamientos alterados de los sistemas TN como activos físicos deben identificar y evaluar riesgos de conformidad con el Reglamento (UE) 2018/762, Anexo II, punto 5.2.1 en relación con el punto 3.1.2. Si, como resultado de ello, se requieren medidas adicionales, estas deben incorporarse también a la gestión de riesgos y deben introducirse instrucciones de trabajo correspondientes para los operadores.
Para F2: Después de que el TN hubiera sido introducido manualmente de nuevo en un campo TN de la estación de Babenhausen tras la deregistración incorrecta explicada, el sistema TN no registró simultáneamente la eliminación automatizada de la deregistración guardada en el bloque 36. Aunque la salida en pantalla del sistema TN mostraba la situación que el despachador deseaba, el registro de la impresora no reflejaba esta situación. En contraste con el Reglamento (UE) 2018/762, Anexo II, punto 4.4.3 d), la información relacionada con la seguridad ya no era, por tanto, coherente. En cambio, los registros manuscritos de mensajes telefónicos de tren permanecen inalterados en un escenario como este, o los cambios acordados son cancelados por las personas implicadas de acuerdo con las especificaciones. La eliminación de un TN que ha sido deregistrado debe permanecer trazable.


## Página 8

Para F4: Según la planificación del sistema TN, el despachador de Babenhausen tenía acceso al campo TN 34, que contiene datos importantes dentro de la autoridad de conocimiento y decisión del despachador de Dieburg sobre los trenes que viajan hacia él. En contraste con el Reglamento (UE) 2018/762, Anexo II, punto 4.4.3 f), esto significaba que era posible eliminar información relacionada con la seguridad sin que el despachador responsable de Dieburg fuera consciente de ello. Para evitar la "manipulación" de datos de los que es responsable otra persona implicada, la autorización de acceso del despachador de Babenhausen debe ser retirada.
## 5.1.3
### Despachador de Babenhausen
Durante la cancelación de la ruta de tren exterior para el DGS 42174, el despachador de Babenhausen notó el avance técnicamente necesario del TN 42174 al bloque 36 aún ocupado y volvió a introducir manualmente el TN 42174 en su vía de estación 301. Según la funcionalidad del sistema de notificación TN 800, el TN 42174 en el campo TN 36 fue eliminado automáticamente de nuevo.
### Factor causal
Para F3: El despachador de Babenhausen no volvió a introducir el TN previamente sobrescrito del DGS 46192 en el campo TN 36. Aunque había información suficiente disponible, no advirtió que el DGS 46192, que había sido liberado previamente, seguía en el bloque 36. En la consola de operaciones en la señal de Babenhausen, el bloque 36 tenía una indicación de ocupación (encendida en rojo). Podía verse en el monitor del TN que el DGS 46192 aún no se había desplazado al siguiente bloque 34, por lo tanto, aún tenía que estar en el bloque 36. Además, la impresora del TN documentó la sobrescritura con la nota "46192 sobrescrito con 42174". Evidentemente, en ese momento, el despachador de Babenhausen ya no era consciente del DGS 46192 y, en consecuencia, no volvió a introducir el TN 46192, que había sido sobrescrito automáticamente de forma involuntaria, en el campo TN 36. En consecuencia, un tren sin TN estaba viajando por la ruta.
### Factor contribuyente
Para F4: Debido a la falla mencionada anteriormente, fue posible que el DGS 46192 cambiara del bloque 36 al bloque 34 sin ser notado por los dos despachadores, y generó allí un número en blanco. El despachador de Babenhausen notó el número en blanco y posiblemente lo atribuyó al avance automático involuntario del TN que había tenido lugar previamente. Aunque el bloque 34 ya no formaba parte de su área de responsabilidad, tenía acceso a este campo TN y podía eliminar el número en blanco. La correspondiente notificación de ocupación relacionada con la señal para el bloque 34 no se le mostró porque estaba fuera de su rango de ajuste. Independientemente de que no fuera responsable, según la directriz 408.0591, sección 3, el acuerdo con el despachador responsable de Dieburg y la consulta de la ubicación de los viajes de tren habrían sido obligatorios antes de la eliminación. La fiabilidad operativa en caso de fallos debe mejorarse y debe concienciarse sobre la necesidad y la aplicación de las normas.
5.1.4
Despachador de Dieburg
Como mostraron las conversaciones de radio de tren, en el momento de la "desaparición" del TN del DGS 46192 causada por Babenhausen, el despachador de Dieburg estaba ocupado con operaciones en otro


## Página 9

punto de su área de ajuste. Es posible que no hubiera observado directamente la eliminación prohibida del número en blanco por parte del despachador de Babenhausen, ni la sobrescritura previa del TN del DGS 46192. Esto no era improbable debido al tamaño del puesto de trabajo y a las tareas de un despachador de enclavamiento informatizado.
### Factores causales
Para F5: Desde la perspectiva del despachador de Dieburg, no había motivo para cuestionar la información (incompleta) en el sistema TN y buscar un tren ausente. Interpretó la indicación de ocupación en el bloque 34 sin un TN guardado como un fallo de conteo de ejes.
Para F6: En consecuencia, el despachador de Dieburg trató el supuesto fallo en el bloque 34 de acuerdo con las normas de la directriz 408.0248 "tren movido más recientemente no detectable". Sin embargo, el despachador no implementó las especificaciones de las directrices. No logró que el DGS 42174, al que se le había dado una instrucción, se detuviera en la señal de entrada 30F y determinar de nuevo la ubicación y el TN. En su lugar, puso prematuramente la señal de entrada 30F a vía libre, como resultado de lo cual el objetivo de protección de las especificaciones de las directrices se vio socavado significativamente. La norma tiene por objeto garantizar que solo un mismo tren pueda recorrer esta sección por completo y que no haya confusión con otro tren que esté circulando por delante de forma no detectada. Sin embargo, la posición abierta significó que el DGS 46192, que esperaba de forma no detectada en la señal de entrada, entró y recorrió la estación en lugar del DGS 42174 esperado, y el despachador de Dieburg realizó a continuación una comprobación de despeje para el DGS 42174 con una evaluación errónea del final del tren del DGS 46192. Según el Reglamento (UE) 2018/762, Anexo II, punto 4.3, dentro de una organización debe garantizarse que los empleados encargados de tareas que afectan a la seguridad sean conscientes de la relevancia, importancia y consecuencias de sus actividades. De acuerdo con el punto 6.1.2 del mencionado Reglamento, el desempeño de tareas relacionadas con la seguridad debe ser supervisado y debe haber una intervención si estas tareas no se están realizando correctamente. La evidencia de formación y formación continua/supervisión del gestor de infraestructura no mostraba claramente si el despachador de Dieburg era consciente de forma adecuada de los objetivos de protección del reglamento.
Para F9: Aunque la observación del final del tren por parte del despachador de Dieburg se llevó a cabo de acuerdo con las normas, debido al error mencionado anteriormente, fue para el tren equivocado. La operación del reinicio del conteo de ejes basada en esto dio lugar a que un estado operativo que era realmente seguro (indicación de ocupación) se convirtiera en un estado potencialmente inseguro (bloque libre), que simultáneamente tenía un nivel de daño potencial muy alto. El objetivo debe ser reducir el nivel de daño posible si existe un riesgo determinado de que los procedimientos de trabajo establecidos se lleven a cabo de forma incorrecta.
Un enfoque temporal apropiado basado en procedimientos para reducir el nivel de daño posible es implementar el principio, que se ha considerado cada vez más en los últimos años, de que "en caso de fallo, el primer tren circula a la vista", incluso si el viaje ha sido efectivamente aprobado con la señal principal, aunque para ello se requerirían acciones auxiliares previas en la señal. Esto no reduce la probabilidad de la situación prohibida de que dos trenes estén en la misma sección, pero circular a la vista reduciría considerablemente el nivel de daño potencial.
Un enfoque técnico sería utilizar desarrollos técnicos ya disponibles en el sector ferroviario para el reinicio del conteo de ejes, como el "reinicio preparatorio del conteo de ejes" ya utilizado por otros gestores de infraestructura. Posibles soluciones técnicas adicionales ya han sido desarrolladas por la industria y se están impulsando mediante estudios. Por ejemplo, un proyecto de investigación del Centro Alemán

## Página 10

para la Investigación del Tráfico Ferroviario [Deutsches Zentrum für Schienenverkehrsforschung, DZSF] de la Autoridad Federal de Ferrocarriles [Eisenbahn-Bundesamt] titulado "Medidas de apoyo cuando se llevan a cabo acciones auxiliares de explotación¹" promete enfoques interesantes.

### Factores contribuyentes

Para F8: Al identificar el final del tren, el operador de Dieburg efectivamente advirtió que el tiempo de recorrido y la velocidad del tren observado no eran coherentes y en ningún caso podían ser el resultado de la conducción a la vista según las reglas. Para resolver esta discrepancia, intentó correctamente ponerse en contacto con el conductor del DGS 42174. El conductor le facilitó repetidamente indicaciones de localización correctas y claras. Aunque, según las normas de procedimiento vigentes, estos informes de localización proporcionan un nivel de respaldo para elementos que presentan averías o no funcionan correctamente, el operador de Dieburg no concedió la credibilidad necesaria a las indicaciones de localización del conductor 42174. Continuó confiando en las pantallas de su equipo de notificación (sistema TN), que no era seguro en términos de señales técnicas. Evidentemente, el operador de Dieburg no logró reflejar la situación y corregirla él mismo si era necesario. Incluso intentó continuamente persuadir al conductor 42174 de que se encontraba en una localización diferente, lo cual, según el análisis de las conversaciones grabadas del radio-tren, este respondió repetidamente, y hacia el final incluso con énfasis, con incomprensión.

Para F7: Un mensaje de tiempo de espera generado por el DGS 46192 a las 03:31 h en el sector de bloqueo 34 no fue procesado por el operador de Dieburg según la normativa, posiblemente por costumbre. El mensaje de tiempo de espera en el sector iluminado en rojo en ese momento (durante o después de la observación del final del tren) era una clara indicación del paso real de un tren y no el resultado de una avería. Aunque las medidas operativas en caso de mensaje de tiempo de espera de cruces monitorizados remotamente tienen como objetivo principal evitar accidentes en cruces, como efecto secundario, el tratamiento del mensaje conforme a las reglas podría haber dado lugar a una reflexión sobre las propias acciones en la situación concreta y podría haber resultado en que el operador de Dieburg advirtiera el DGS 46192. La fiabilidad operativa en caso de averías debe mejorarse y debe concienciarse sobre la necesidad y la aplicación de las reglas.

### Factores sistémicos

Para F5: A juzgar por las conversaciones del radio-tren, el operador de Dieburg asumió que existía una avería de conteo de ejes dejada por un tren que había circulado previamente en el sector de bloqueo 34. Las normas en la directriz 408.0591 sección 3 no contienen instrucciones sobre qué hacer si no se muestra ningún TN en un campo TN de un sector que se muestra como ocupado. Ni siquiera remiten a las instrucciones de trabajo para una indicación de ocupación identificada (aquí directriz 408.0248) de un sector de vía. Las normas en la directriz 408.0591 deberían complementarse para el escenario "sin TN en el campo TN" con indicación de ocupación simultánea.

Para F6: El procedimiento operativamente importante para proteger contra la confusión de un tren entrante con un tren que aún avanza sin ser detectado en el mismo sector depende de las acciones correctas de una sola persona. El proceso debería diseñarse de forma adecuada para que el operador se vea obligado a esperar el mensaje de implicación y resultado de otra persona implicada, por ejemplo el conductor, para protegerse de sus propias acciones incorrectas.

Para F7: Evidentemente, los operadores de Dieburg en general no tenían la conciencia necesaria sobre la necesidad de aplicar las reglas en caso de tiempo de espera. Los riesgos de estados operativos no deseados con

¹ DZSF - proyectos - Título en alemán: Unterstützungsmaßnahmen bei der Durchführung von betrieblichen Hilfshandlungen (bund.de) fechado el 09/08/2023


## Página 11

resultantes avisos técnicos frecuentes obviamente no se destacaron suficientemente durante la planificación de la infraestructura, y las consecuencias de ello no se consideraron. Según el Reglamento (UE) 2018/762 Anexo II punto 5.2.1, la organización debe gestionar los riesgos de seguridad asociados a los activos físicos y cumplir los requisitos relacionados con los factores humanos. Donde los trenes puedan detenerse, la aparición de mensajes de tiempo de espera ya debe considerarse al planificar la infraestructura.

Para F8: En caso de información de localización contradictoria del conductor por una parte y de los sistemas técnicos, como el sistema TN, por otra, hay dos fuentes equivalentes disponibles para el operador. Como decisor, tiene libertad para juzgar y seleccionar qué información concede credibilidad. Por lo tanto, debería incorporarse un decisor adicional que utilice información fiable con el fin de garantizar la aclaración de la información correcta. Hasta que exista una decisión de este decisor, continuar las operaciones no parece aconsejable.

## 5.1.5

### Conductor 46192

El DGS 46192 permaneció estacionado durante unos 21 minutos en la señal de entrada 30F de la estación de Dieburg y también durante unos 25 minutos hasta el incidente en la señal de entrada de Darmstadt-Kranichstein, sin comunicarse con el operador en un plazo de cinco minutos en cada caso.

### Factor contribuyente

Para F10: Si el conductor 46192 hubiera preguntado al operador de Dieburg por el motivo de la detención durante estos períodos según las especificaciones de la normativa, su TN habría vuelto a llamar la atención del operador de Dieburg. Debe señalarse que esta normativa es en gran medida opcional. Durante el período en consideración, tampoco fue plenamente implementada por otros conductores de otros trenes no implicados en el incidente, porque antes de emprender el recorrido ya habían sido informados sobre dificultades operativas previstas. No fue posible determinar si al conductor 46192 también se le había facilitado esta información.

## 5.1.6

### Observaciones sobre los sistemas TN

El procedimiento telefónico de mensajes de tren es utilizado por el operador para información relacionada con la seguridad sobre los recorridos de trenes y para la programación de estos recorridos. El sistema técnico de seguridad se utiliza en gran medida para proteger la sucesión de trenes. La información sobre qué recorrido de tren con qué características se aproxima a una estación o parada y cómo debe ser tratado allí según las especificaciones de programación debe considerarse relacionada con la seguridad, incluso si existe un sistema de bloqueo de señalización efectivo. En caso de avería como tarde, el procedimiento telefónico de mensajes de tren tiene entonces también la única tarea de garantizar que la sucesión de trenes se desplace con el intervalo correcto. La transición del modo normal al modo de avería es, por tanto, crítica en relación con la corrección y coherencia obligatorias de los datos que las personas implicadas continúan utilizando. Los sistemas técnicos incorporados a un sistema de trabajo relacionado con la seguridad deben, por tanto, crearse de manera que, en la transición al modo de avería, proporcionen directamente información fiable sobre las operaciones. Si es necesario, deben utilizarse procesos de trabajo complementarios para comparar la corrección y coherencia de los datos disponibles con el estado operativo actual. Además, los sistemas técnicos de apoyo no deberían ser una fuente de error en sí mismos. La conciencia del gestor de infraestructura es, por tanto, muy importante para las


## Página 12

relaciones entre la planificación adecuada, el rendimiento y la supervisión de las operaciones y los procedimientos inherentes.

Los sistemas TN no son sistemas de notificación seguros desde una perspectiva de señalización técnica, pero, en el caso de los enclavamientos basados en ordenador en particular, están integrados en indicaciones técnicas de señalización seguras y se muestran en los monitores de explotación. El operador de Dieburg no parecía ser plenamente consciente de la discrepancia entre los dos tipos de indicación. Creía que la indicación TN incorrecta y el avance del TN 42174 eran más importantes que la información de localización clara y correcta del conductor 42174. Por lo tanto, parece necesario concienciar al personal de explotación sobre la significación limitada de los sistemas TN, y también someter a escrutinio crítico la organización de la interfaz hombre-máquina.

A pesar de la contradicción no resuelta entre sus indicaciones técnicas de notificación y la información de localización del conductor 42174, el operador de Dieburg produjo un reinicio de bloqueo para el sector 34. La información disponible de la indicación no segura de su sistema TN fue la base para que el operador realizara el reinicio de conteo de ejes, es decir, para una intervención en la tecnología de señalización segura que tuvo graves consecuencias. No deben realizarse intervenciones en la tecnología de señalización segura basándose únicamente en hallazgos obtenidos a partir de indicaciones en equipos de notificación que no son seguros desde una perspectiva de señalización técnica.

## 5.1.7

### Conclusión

Funciones operativamente implausibles del sistema de notificación TN 800 en Babenhausen en combinación con errores operativos del operador de Babenhausen dieron lugar a que un tren sin un TN guardado en el sistema TN circulara en el recorrido entre Babenhausen y Dieburg. Los datos guardados en el sistema TN no reflejaban las operaciones reales y animaron al operador de Dieburg a tomar decisiones incorrectas basándose en esta información. A pesar de otras indicaciones de un recorrido de tren, el operador de Dieburg evaluó incorrectamente el informe técnico de ocupación del sector de bloqueo 34 como una avería de conteo de ejes. Errores adicionales en la aplicación de las reglas en combinación con la dependencia exclusiva de la corrección de la indicación del sistema TN, que no es segura en términos de tecnología de señalización, dieron lugar a una grave mala interpretación de la situación operativa real por parte del operador de Dieburg. Como resultado de ello, reinició el sector de bloqueo 34, lo que finalmente provocó la colisión de los trenes.

Todo el sistema de trabajo para el procesamiento y transmisión de mensajes de tren es directamente relevante para la seguridad. Debe garantizarse que este sistema siempre proporcione seguridad suficiente, incluso al cambiar del modo normal al modo de avería. Esto se refiere, en particular, a las rutinas para añadir o corregir información que fue procesada, transmitida o archivada previamente de forma automática, y que entonces, en particular cuando ocurren averías o se presume que han ocurrido, es un nuevo factor a incorporar en las decisiones posteriores sobre las acciones futuras del personal de explotación.

## 5.2

### Medidas adoptadas desde el incidente

Tras el incidente, DB Netz AG emitió la orden de servicio 2022-46 a las señales de Babenhausen y Dieburg. Esta regulaba el procedimiento operativo para liberar un itinerario en dirección a Dieburg.

DB Netz AG está examinando si puede haber un desarrollo posterior del software para el sistema de notificación TN 800 en Babenhausen. No es posible utilizar una versión de software anterior.

## Página 13

DB Netz AG ha adoptado medidas relacionadas con la creciente aparición de mensajes de tiempo de espera. El jefe de tráfico ha recibido formación y supervisión específica en relación con este asunto. Al mismo tiempo, DB Netz AG está examinando medidas adicionales para eliminar la causa de los mensajes frecuentes, p. ej. la modificación de la ubicación de las señales para las señales de bloque.
## 5.3 
### Observaciones adicionales 
Ninguna
## 6 
### Recomendaciones de seguridad 
Se formulan las siguientes recomendaciones de seguridad de conformidad con el apartado 6 del EUV [reglamento alemán de investigación de accidentes ferroviarios] y el artículo 26.2 de la Directiva (UE) 2016/798: 
N.º.
Destinatario y recomendación de seguridad
Empresa a la que se refiere
01/2023
Autoridad de seguridad:
IM
Se recomienda que se examine y modifique el sistema de trabajo para el procesamiento y la transmisión de mensajes de tren, de modo que su información cumpla siempre los requisitos establecidos en el Reg. (UE) 2018/762, Anexo 2, punto 4.4.3, en particular durante la transición entre procesos automatizados y manuales. 
02/2023
Autoridad de seguridad:
IM
Se recomienda que los procesos de planificación, ejecución y aprobación de las funciones de los sistemas TN se examinen y mejoren de conformidad con el Reg. (UE) 2018/762 Anexo II punto 5.2.1, incluida la gestión de cambios y de riesgos asociada, a fin de garantizar que el activo físico se integre de forma segura en los sistemas de trabajo.  
03/2023
Autoridad de seguridad:
IM
Se recomienda que, para garantizar la función protectora del procedimiento de trabajo «el mismo tren ha entrado en un tramo y ha salido de él de nuevo» de conformidad con el Reg. (UE) 2018/762 Anexo II punto 3.1.1.1, se determinen los riesgos en caso de errores por parte de las personas implicadas y se mejore el procedimiento de trabajo. 


## Página 14

| 04/2023 | Autoridad de seguridad: Se recomienda que, de conformidad con el Reg. (UE) 2018/762 Anexo II punto 3.1.1.1, se determinen los riesgos en caso de discrepancias entre la ubicación de un tren asumida por el jefe de tráfico y la ubicación comunicada por el maquinista, y que se desarrollen procedimientos de trabajo adecuados para la continuación segura de la explotación. | IM |
| 05/2023 | Autoridad de seguridad: Se recomienda que se sigan desarrollando las condiciones técnicas para la eficacia de la acción de control del operador de reinicio de un contador de ejes, a fin de minimizar aún más o excluir los riesgos de acciones de control del operador exitosas e intempestivas. Hasta que estas medidas se implementen técnicamente, y a fin de minimizar los daños potenciales, se recomienda que se implementen soluciones compensatorias basadas en procedimientos. | IM |
