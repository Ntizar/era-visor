---
pais: HU
anio: 2021
idioma_origen: HU
md_origen: md/HU/2021/HU-10054_Final_Report_HU.md
md5_origen: 54fdced11d3321bdb70b5176ffc6b7ae
modelo: mimo-v2.6-flash
bloques: 5
chars: 50118
ratio_longitud: 1.11
tokens_in: 21948
tokens_out: 13359
verificacion: ok
fecha_proceso: 2026-11-22
generador: traducir_md_es.py (traducción IA + verificación numérica)
notas_cifras: ["página 3: original bilingüe: se compara contra el idioma principal (HU)", "página 6: original bilingüe: se compara contra el idioma principal (HU)", "página 7: original bilingüe: se compara contra el idioma principal (HU)", "página 10: original bilingüe: se compara contra el idioma principal (HU)", "página 11: original bilingüe: se compara contra el idioma principal (EN)", "página 12: original bilingüe: se compara contra el idioma principal (HU); cifras cortas: 2/19"]
---
## Página 1

MINISTERIO DE TECNOLOGÍA E INDUSTRIA 
ORGANISMO DE SEGURIDAD DEL TRANSPORTE 
INFORME FINAL 
2021-0459-5 
(HU-10054) 
Evento ferroviario imprevisto / Paso de señal 
Gödöllő, 17 de mayo de 2021 


## Página 2

### Principios básicos de la investigación técnica 
El objetivo de la investigación técnica es determinar las causas y circunstancias de los accidentes ferroviarios graves, de los accidentes ferroviarios y de los eventos ferroviarios imprevistos, así como promover las medidas técnicas necesarias para la prevención de casos similares y formular recomendaciones. La investigación técnica no tiene como objetivo, en ninguna forma, la determinación ni el establecimiento de la culpa o de la responsabilidad. 
Las conclusiones de la investigación se basan en la evaluación por parte del OSB de las pruebas disponibles y obtenidas durante la misma, teniendo en cuenta los principios de un procedimiento justo e imparcial. El informe final únicamente nombra a las personas implicadas en el accidente en función del puesto de trabajo y de las funciones que desempeñaban en el momento del evento. 
El OSB está obligado a conservar los datos que lleguen a su conocimiento durante la investigación técnica y no está obligado a hacerlos accesibles a otra autoridad, respecto a los cuales el titular de los datos hubiera podido denegar su comunicación con base en la normativa.1 
El Informe final no tiene carácter vinculante y contra el mismo no puede iniciarse ningún procedimiento de recurso. 
El Organismo de Seguridad del Transporte llevó a cabo la investigación 
- 
con arreglo a la Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de transporte por vía navegable y de otros eventos de transporte (en adelante: Ley Kbvt.); 
- 
con arreglo al Reglamento de Ejecución (UE) 2020/572 de la Comisión (24 de abril de 2020) sobre la estructura de los informes que debe seguirse en los informes de investigación sobre accidentes ferroviarios y eventos imprevistos; 
- 
con arreglo al Reglamento 24/2012. (V.8.) del Ministerio de Desarrollo Nacional (NFM) sobre las normas detalladas de la investigación técnica de los accidentes ferroviarios graves, de los accidentes ferroviarios y de los eventos ferroviarios imprevistos, así como de la investigación del operador; 
- 
y, en defecto de disposiciones divergentes de la Ley Kbvt., con la aplicación adecuada de las disposiciones de la Ley CL de 2016 sobre el procedimiento administrativo general. 
La Ley Kbvt. y el Reglamento 24/2012. (V.8.) del NFM sirven conjuntamente para el cumplimiento del acto jurídico de la Unión, la Directiva (UE) 2016/798 del Parlamento Europeo y del Consejo (11 de mayo de 2016) relativa a la seguridad ferroviaria (en adelante: Directiva de seguridad ferroviaria). 
La competencia del Organismo de Seguridad del Transporte se basa en el Decreto 230/2016. (VII. 29.) del Gobierno sobre la designación del organismo de seguridad del transporte y sobre la extinción del Organismo de Seguridad del Transporte con sucesión universal. 
La investigación técnica es independiente de las demás actuaciones administrativas, de infracción o penales iniciadas en relación con el accidente de transporte o con el otro evento de transporte. 
### Derechos de autor 
El informe final fue emitido por: 
### Ministerio de Tecnología e Industria, Organismo de Seguridad del Transporte 
1103 Budapest, Kőér u. 2/A. 
www.kbsz.hu 
kbszvasut@tim.gov.hu 
El informe final o sus partes pueden utilizarse en cualquier forma, con excepción de las previstas en la normativa, siempre que los detalles conserven su contexto de contenido y se identifique con precisión la fuente. 
1con arreglo al apartado 18.§ (1) y (6) de la Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de transporte por vía navegable y de otros eventos de transporte 


## Página 3

### DEFINICIONES Y ABREVIATURAS 
ERAIL 
Base de datos de accidentes de la Agencia Ferroviaria de la Unión Europea (el identificador ERAIL del evento es el número indicado entre paréntesis en la portada, bajo el identificador del OSB) 
emisión de señal 
la función de transmisión de datos integrada en la vía férrea, que transmite al puesto de conducción información relativa a la imagen de señalización del señal aproximado 
OSB 
Organismo de Seguridad del Transporte del Ministerio de Tecnología e Industria 
Kbvt. 
Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de transporte por vía navegable y de otros eventos de transporte 
MÁV Zrt. 
Ferrocarriles Estatales Húngaros, S.A. 
MFB 
Dispositivo de A bordo de Locomotora (dispositivo que desempeña funciones de seguimiento de tren, registro de datos y libreta de circulación electrónica) 
psz. 
número de vehículo 
TIM 
Ministerio de Tecnología e Industria 
en tramo de vía con emisión de señal instalada para el sistema de influencia en el tren 
el dispositivo de influencia en el tren mantiene comunicación entre la locomotora y los señales principales fijos, en cuyo caso el señal del puesto de conducción repite la preseñalización relativa al señal principal aproximado, es decir, aparece el espectro de color y/o la inscripción que indica la velocidad máxima permitida aplicable en el señal principal aproximado, y el maquinista está obligado a regular la velocidad del tren en consecuencia, además, si la locomotora ha pasado un señal principal que emite la señal «¡Detenerse!», con una velocidad superior a 15 km/h el dispositivo provoca un frenado forzoso 
Vb 
Comisión de Investigación 


## Página 4

### ÍNDICE 
1. 
RESUMEN ............................................................................................................................................. 5 
2. 
EL PROCEDIMIENTO DE INVESTIGACIÓN Y SUS RELACIONES................................................................ 6 
2.1 
Inicio de la investigación .................................................................................................................. 6 
2.2 
Motivo del inicio de la investigación .................................................................................................. 6 
2.3 
Alcance y límites de la investigación .................................................................................................. 6 
2.4 
La Comisión de Investigación ............................................................................................................. 6 
2.5 
Procesos de comunicación y consulta ................................................................................................. 7 
2.6 
Colaboración ...................................................................................................................................... 7 
2.7 
Métodos de investigación ................................................................................................................... 7 
2.8 
Dificultades de la investigación .......................................................................................................... 7 
2.9 
Contacto con las autoridades judiciales .............................................................................................. 7 
3. 
DESCRIPCIÓN DEL EVENTO ................................................................................................................. 8 
3.1 
Descripción del evento ...................................................................................................................... 8 
3.2 
Cronología del evento ...................................................................................................................... 11 
4. 
ANÁLISIS DEL EVENTO ......................................................................................................................... 12 
4.1 
Funciones de las personas y de las organizaciones ........................................................................... 12 
4.2 
Los vehículos y los dispositivos técnicos .......................................................................................... 13 
4.3 
Factores humanos ........................................................................................................................... 17 
4.4 
Eventos similares anteriores ............................................................................................................. 20 
5. 
CONCLUSIONES .................................................................................................................................. 21 
5.1 
Resumen ......................................................................................................................................... 21 
5.2 
Observaciones adicionales ................................................................................................................ 21 
5.3 
Lecciones aprendidas ....................................................................................................................... 21 
6. 
RECOMENDACIÓN DE SEGURIDAD ...................................................................................................... 22 
7. 
OPINIONES DIVERGENTES ................................................................................................................. 22 
ANEXOS ................................................................................................................................................. 23 
Anexo 1 
El registrador de datos del vehículo ferroviario ........................................................................ 23 
Anexo 2 
La normativa y las instrucciones citadas ................................................................................ 24 


## Página 5

### 1. 
### RESUMEN 
En la estación de Gödöllő, el 17 de mayo de 2021, a las 11:16 horas, el tren n.º 3135, tras su salida, pasó sin autorización el señal de salida K4 que emitía la señal «¡Detenerse!» y cruzó el desvío n.º 22. El tren circuló hasta la estación de Isaszeg. Como consecuencia del evento no se produjeron lesiones personales ni se puso en peligro ningún tren. 
Durante la investigación, la CI determinó que el tren disponía de autorización para llegar hasta la estación de Isaszeg, sin embargo, la ruta de salida aún no había sido dispuesta. Cuando llegó la hora de la salida, los movimientos del agente de circulación externo que se encontraba en el andén, al final del tren, se asemejaron durante un breve instante —de forma involuntaria— a la señal «Llamada», lo que el personal de acompañamiento interpretó erróneamente y, tras dar la señal «Listo para la salida», subió al tren. El maquinista dedujo erróneamente de lo anterior que se cumplían las condiciones para la salida del tren y partió con su tren. 
La CI identificó como causa del evento que el maquinista partió con el tren sin autorización y en ausencia de una señal que autorizara el paso por el señal de salida. 
Contribuyó a la ocurrencia del evento que la emisión de señal, tras el cambio de sentido, no funciona para el tren que sale hasta que se haya dispuesto la ruta desde la vía correspondiente, por lo que en el señal del puesto de conducción tampoco aparece la señal relativa al señal en posición «¡Detenerse!», además, al pasar junto al señal que emite la señal «¡Detenerse!» tampoco se produce frenado forzoso. 
El caso pone de manifiesto que, debido a la configuración del sistema de emisión de señal empleado, el sentido de circulación del vehículo y el sentido de alimentación de las señales de vía deben ser opuestos para un correcto funcionamiento, sin embargo, con el cambio en el sentido de circulación de los trenes, el sentido de alimentación no se invierte. En tal caso, el dispositivo de influencia en el tren funciona como si se tratara de un tramo de vía sin emisión de señal instalada, por lo que los maquinistas deben circular con conocimiento de ello. 
En relación con el caso, el OSB no emite ninguna recomendación de seguridad.

## Página 6

### 2.
### PROCESO Y CONTEXTO DE LA INVESTIGACIÓN
### 2.1
### Inicio de la investigación
El caso fue comunicado a la guardia de la KBSZ por el Jefe de Control de Red de MÁV Zrt. el 17 de mayo de 2021 a las 11:36 (20 minutos después de la ocurrencia).
El jefe de guardia de la KBSZ ordenó de inmediato una inspección in situ. Con base en las observaciones de la inspección, el jefe de la KBSZ decidió iniciar una investigación técnica.
### 2.2
### Motivo del inicio de la investigación
La Autoridad de Seguridad del Transporte, de conformidad con el apartado 7 § (1) del Kbvt.,
1. investiga los accidentes ferroviarios graves;
2. puede investigar aquellos accidentes ferroviarios y sucesos ferroviarios imprevistos que, a su juicio, en circunstancias ligeramente diferentes podrían haber conducido a accidentes graves, ponderando
a) la gravedad del accidente o del suceso ferroviario imprevisto,
b) si forma parte de una serie de sucesos de importancia desde el punto de vista del sistema en su conjunto,
c) el efecto sobre la seguridad ferroviaria,
d) las solicitudes de los operadores de la red de vías férreas, de las compañías ferroviarias, de las autoridades nacionales de seguridad o de los Estados miembros;
e) si la investigación puede aportar lecciones en materia de seguridad.
La presente investigación se inició con base en el apartado 2. b) anterior (en consonancia también con el artículo 20, apartado 2, letra b, de la Directiva de seguridad ferroviaria UE 2016/798), porque durante el suceso no se produjeron lesiones personales ni daños materiales, pero los pasos de señal sin autorización conllevan un riesgo muy alto de los mismos y son frecuentes en la red. La investigación y la extracción de lecciones permiten mitigar el riesgo de accidentes del tráfico ferroviario.
### 2.3
### Alcance y limitaciones de la investigación
El objetivo de la investigación fue la reconstrucción cronológica del desarrollo del suceso, la identificación de los factores humanos, organizativos y técnicos que influyeron en la actividad del personal y en el funcionamiento de los equipos técnicos, la determinación de las causas directas e indirectas y la exposición de las lecciones necesarias.
### 2.4
### Comisión de investigación
El jefe de la KBSZ designó la siguiente Comisión de investigación para la investigación del suceso ferroviario:
presidente
Demjén Péter
investigador de accidentes
miembro
Duli Ádám
investigador de accidentes
La Comisión de investigación contaba con las competencias necesarias para realizar la investigación, por lo que no fue necesario recurrir a expertos externos.


## Página 7

### 2.5
### Procesos de comunicación y consulta
La Comisión de investigación escuchó en el lugar al personal del tren y al personal de la estación.
### Proyecto de informe final
La KBSZ envió el proyecto de informe final a
- MÁV Magyar Államvasutak Zrt.,
- MÁV-Start Zrt.,
- la Subdirección General de Autoridad Ferroviaria del TIM.
La Subdirección General de Autoridad Ferroviaria del TIM formuló observaciones al proyecto de informe final enviado, que se referían a aclaraciones menores.
### 2.6
### Colaboración
Las organizaciones implicadas pusieron a disposición de la Comisión de investigación los datos y documentos que esta consideró necesarios y solicitó.
### 2.7
### Métodos de investigación
Para la investigación, la Comisión de investigación utilizó
- las observaciones de la inspección in situ realizada el 17 de mayo de 2021;
- las grabaciones de las cámaras de videovigilancia instaladas en el tren y en la estación;
- las conversaciones telefónicas grabadas del regulador de línea;
- los datos registrados por el registrador electrónico de datos de marcha y el MFB del automotor;
- las audiencias también citadas en el capítulo 2.5.
### 2.8
### Dificultades de la investigación
En la estación de Gödöllő, la grabación de audio de la mesa de comunicación no funcionó debido a problemas de configuración, por lo que el contenido de la llamada telefónica entre el regulador y el maquinista solo pudo conocerse a través de las declaraciones de los implicados. Este mismo equipo habría grabado también la comunicación por radio entre el regulador y los agentes de tráfico exteriores.
### 2.9
### Contacto con las autoridades judiciales
No fue necesario el contacto con las autoridades judiciales.


## Página 8

### 3.
### DESCRIPCIÓN DEL SUCESO
### 3.1
### Descripción del suceso
En la estación de Gödöllő, el 17 de mayo de 2021 a las 11:16, el tren n.º 3135, tras su salida, pasó sin autorización la señal de salida K4, que indicaba la orden «¡Alto!», y desvió el desvío n.º 22. El tren llegó hasta la estación de Isaszeg. Como consecuencia del suceso no se produjeron lesiones personales ni se puso en peligro ningún tren.
## 3.1.1
### Tipo de suceso
Tipo de suceso:
### Suceso ferroviario imprevisto
Naturaleza del suceso:
### Paso de señal
## 3.1.2
### Fecha y lugar del suceso
### Fecha del suceso: 17 de mayo de 2021, 11:16
Lugar:
red nacional de vías férreas
### Línea férrea n.º 80 Budapest – Miskolc – Sátoraljaújhely
### Estación de Gödöllő
Figura 1: lugar del suceso (mapa: ArcGIS WorldTopoMap)
## 3.1.3
### Escenario del suceso
La estación de Gödöllő es la estación intermedia de la línea principal n.º 80 Budapest – Hatvan – Miskolc – Sátoraljaújhely. La estación registra un tráfico importante de pasajeros de larga distancia y de cercanías. Además de las dos vías principales de paso (II, V) y de las vías principales que las rodean (I, VI), dispone de dos vías muertas accesibles desde el punto de partida, que se utilizan para la maniobra de trenes de cercanías que circulan entre Budapest-Keleti y Gödöllő.


## Página 9

Figura 2: Red de vías y itinerario recorrido por el tren
En el momento del hecho el tiempo era el propio de la estación del año. Cuando el tren partió estaba lloviendo, y con luz natural diurna la visibilidad no estaba limitada.
## 3.1.4
### Consecuencias
### Lesiones personales
| Lesión | Personal | Pasajeros | Usuarios de paso a nivel | Ajenos | Otros |
| Mortales | - | - | - | - | - |
| Graves | - | - | - | - | - |
| Leves | - | - | - | - | - |
| No lesionados | 3 | aprox. 15 | - | - | - |
### Daños materiales
No se produjeron daños materiales.
### Daños medioambientales
No se produjeron daños medioambientales.
## 3.1.5
### Otras consecuencias
El tren n.º 3135 no llegó a la estación de Isaszeg, cuyos pasajeros fueron trasladados por el tren n.º 5507. Otros dos trenes de pasajeros no llegaron parcialmente a su destino y tres trenes tuvieron un retraso total de 23 minutos.
## 3.1.6
### Organizaciones y personas implicadas
El operador de la red de vías férreas es MÁV Magyar Államvasutak Zrt. En la estación, en el momento del hecho, prestaban servicio un regulador de tráfico y un agente de tráfico exterior.
El tren n.º 3135 era operado por MÁV-Start Zrt. En el tren prestaban servicio un maquinista, un revisor jefe y un revisor.


## Página 10

## 3.1.7
### Los trenes
En el suceso se vio implicado el tren regional de pasajeros n.º 3135, circulado con el automotor n.º de matrícula 94 55 2415 030-3 en el trayecto Gödöllő – Budapest Keleti:
composición: 2 unidades
longitud: 149 m
masa sin carga: 308 t
La capacidad de frenado del tren era la adecuada.
## 3.1.8
### La infraestructura
En la estación funciona un enclavamiento electrónico Elektra 2, cuya interfaz de mando se encuentra en la oficina de tráfico. Las vías de la estación están electrificadas y está implantada la señalización para el control de la circulación de trenes. La distancia entre el extremo delantero del tren detenido en la vía IV y la señal K4 era de aproximadamente 30 metros.
## 3.1.9
### Situación de tráfico
A las 11:02 circuló por la vía II el tren n.º 199; a continuación, a las 11:12 llegó a la vía III el tren n.º 3114, y el desvío n.º 22 estaba dispuesto en dirección de desvío en ese itinerario, por lo que el tren n.º 3135, que partía de la vía IV y que se vio implicado en el suceso, lo desvió al partir.


## Página 11

### 3.2
### Cronología del suceso
Con base en las pruebas recabadas, el desarrollo real del suceso puede reconstruirse como sigue:
## 3.2.1
### Sucesos anteriores al suceso
## 10:44
la composición y el personal implicados en el suceso llegaron a la vía IV como tren n.º 3162;
## 11:12
llegó a la vía III el tren n.º 3114; el agente de tráfico exterior entregó por escrito una orden al maquinista del tren en el extremo del andén;
## 3.2.2
### Desarrollo del suceso
## 11:15:38
el agente de tráfico exterior, con el dispositivo de señalización de salida en la mano (sosteniéndolo horizontalmente, con el lado que emite la señal hacia el personal de acompañamiento durante unos 2 segundos), se inclinó hacia delante en el extremo del tren observando la señal de salida, mientras el personal del tren emitía la señal «Listo para la salida»;
## 11:16:00
el tren n.º 3135 partió de la vía IV;
el agente de tráfico exterior emitió la señal «¡Alto!» con el dispositivo de señalización de salida;
el tren pasó por los desvíos a 40 km/h, desvió el desvío n.º 22, que estaba dispuesto incorrectamente para él, y a continuación aceleró a 58 km/h;
## 11:17:50
el regulador de tráfico llamó por teléfono al maquinista del tren n.º 3135, que se detuvo tras recorrer 1050 metros.
## 3.2.3
### Sucesos posteriores al suceso
## 11:18:38
el tren reanudó la marcha con el fin de liberar la vía;
## 11:23
se detuvo ante la señal de entrada de la estación de Isaszeg y, tras la maniobra de la señal, entró en la estación;
## 11:26:00
el tren se detuvo en la vía II de la estación de Isaszeg


## Página 12

### 4.
### ANÁLISIS DEL SUCESO
### 4.1
### Funciones de las personas y organizaciones
## 4.1.1
### Autorización
En la estación, la autorización para la salida de los trenes corresponde al agente de tráfico exterior. Para la autorización, el regulador de tráfico da instrucción por radio al agente de tráfico exterior una vez establecido el itinerario de los trenes y aparecida en la señal de salida la señal que autoriza la circulación, la cual debe ser repetida por este. Si aparece la señal que autoriza la circulación pero el regulador no da instrucción, el empleado que debe autorizar debe solicitar confirmación por radio. Según la declaración del personal de la estación y las observaciones de la Comisión de investigación², en la práctica esto es efectivamente lo que ocurre.
## 4.1.2
### Maquinista
En el caso examinado, las condiciones para la salida del tren por parte del maquinista son:
- Llegada de la hora de salida según el horario;
- Existencia en la señal de salida de la señal que autoriza la circulación;
- Señal «Llamada para la salida» por parte del agente de tráfico.
En el suceso examinado no se cumplieron las condiciones anteriores, lo que se analiza con mayor detalle en el capítulo 4.3.2.1.
## 4.1.3
### Personal de acompañamiento
En los puestos de servicio en los que la autorización de los maquinistas de los trenes de pasajeros corresponde a los revisores jefes, la condición para emitir la señal «Listo para la salida» es la existencia de la señal que autoriza la circulación de la señal principal del tren, ya que la observación de esta también es tarea de quien autoriza (Anexo 2). Sin embargo, en el suceso examinado fue el personal de tráfico de la estación quien autorizó a los maquinistas mediante la maniobra de señales y el dispositivo de señalización de salida, por lo que los revisores no tenían obligación de observar las señales.
² En las conversaciones telefónicas grabadas se oye que efectivamente siguen esta práctica, y las propias experiencias adicionales de la Comisión de investigación también lo confirman.

## Página 13

### 4.2 
### Los vehículos y los equipos técnicos 
## 4.2.1 
### Equipo de influencia en el tren EVM-120 
En el tren implicado en el suceso funcionaba el equipo de influencia en el tren EVM-120, el cual en el momento del suceso no estaba desconectado. 
En un tramo de vía no equipado para la emisión de señales, el equipo de influencia en el tren desempeña únicamente la función de control de vigilancia. En un tramo de vía equipado para la emisión de señales, si no hay alimentación desde la dirección contraria conforme a la dirección de circulación, el equipo funciona igual que en un tramo de vía no equipado para la emisión de señales. 
En un tramo de vía equipado para la emisión de señales, bajo la acción de las señales procedentes de la vía, el equipo convierte la información transmitida por los impulsos en órdenes de velocidad, y proporciona información al maquinista en forma de imágenes de colores y pictogramas mostrados en el indicador de la cabina de conducción: 

| El nombre de la señal | Imagen del indicador digital de la cabina de conducción | Significado de la señal transmitida por la señal para el maquinista |
| --- | --- | --- |
| Impulso 0 | | El tren ha pasado junto a la señal principal que da la indicación «¡Alto!». |
| Impulso 1 | | En la siguiente señal hay indicación «¡Alto!». Prepararse para detenerse. |
| Impulso 2 | | En la siguiente señal hay indicación que autoriza la circulación con velocidad reducida (40 km/h). |
| Impulso 3 | | En la siguiente señal hay indicación que autoriza la circulación con velocidad reducida (80 km/h). |
| Impulso 4 | | En la siguiente señal hay indicación que autoriza la circulación sin reducción de velocidad. |
| Impulso X | | No llega ninguna señal evaluable desde la vía. El equipo es inutilizable, o el tren ha llegado desde un tramo de vía no equipado para influencia en el tren a un tramo equipado para influencia en el tren pero ocupado, o a un tramo de vía que no está equipado para influencia en el tren. |

La parada automática del tren solo se produce en la transición de señal del impulso 1 al impulso 0, si la velocidad del vehículo es superior a 15 km/h y la dirección de la alimentación era la correcta. 
Si en la señal que se aproxima hay indicación que impone velocidad reducida o que prohíbe la circulación, el equipo controla la vigilancia del maquinista cada 200 metros, advirtiéndole mediante una llamada de vigilancia comprimida de la necesidad de una intervención reguladora de la velocidad. En el presente caso, debido a la proximidad de la señal, el papel de las llamadas de vigilancia comprimidas no habría podido ejercerse. 


## Página 14

## 4.2.2 
### Emisión de señales al cambiar de dirección 
La vía IV es una vía muerta equipada para la emisión de señales. Para los trenes que entran en ella, la emisión de señales se realiza desde la dirección de la señal V4. El cambio de la dirección de alimentación de la emisión de señales se lleva a cabo mediante la establecimiento del itinerario de salida; a partir de entonces, la alimentación se realiza desde la dirección de la señal K4. 
En el momento del suceso, en el indicador de la cabina de conducción del automotor eran visibles tres líneas horizontales (Anejo 1). El equipo no detectó ninguna señal evaluable desde la vía, lo que indica que el cambio de la dirección de alimentación no se había producido antes de la partida del tren, es decir, que el itinerario de salida no había sido establecido, y por tanto, debido a la concepción del equipo, no podía haber en la señal una imagen indicativa que autorizara la circulación. 
Figura 3: Indicación visible en el indicador de la cabina de conducción en el caso de una señal de salida que da la indicación «¡Alto!», sin establecer el itinerario 
El equipo de influencia en el tren (4.2.1) solo provocaría una frenada forzada al pasar junto a una señal que da la indicación «¡Alto!» en el caso de que, al aproximarse a la señal en posición «¡Alto!», se produjera la alimentación del impulso 1 y, a continuación —al pasar junto a la señal—, la señal desapareciera. En el caso de la vía IV, la alimentación del impulso 1 no se produjo para un tren que cambiaba de dirección en la vía desde la dirección de la señal K4, ya que la inyección de las señales solo habría comenzado cuando se establece el itinerario de salida en el equipo. 


## Página 15

Figura 4: Indicación mostrada en el indicador de la cabina de conducción con el itinerario establecido 
Para el maquinista, la información transportada por el impulso 1 tendría aquí una importancia capital. Si la alimentación de las señales se hubiera realizado desde la dirección de la señal K4, en el indicador de la cabina de conducción habría aparecido la indicación «0». En este caso, una vez iniciado el tren y por encima de 15 km/h, el equipo habría detenido el tren con frenada forzada al superar la señal. 
De la concepción del aparato de enclavamiento se desprende que el maquinista no puede recibir la indicación «0» (impulso 1) —que es también la base para detener el tren que supera una señal en posición «¡Alto!»— antes de que se establezca el itinerario, y por tanto la función de parada del tren no puede llegar a materializarse. Pues la dirección de inyección solo cambia cuando se ha establecido para el tren el itinerario de salida. Sin embargo, esto suele ir seguido inmediatamente por el paso de la señal de salida a posición que autoriza la circulación, y entonces ya no se necesita la función de parada del tren (esta solo funcionaría en una señal que eventualmente retrocediera). Debido a la concepción del equipo, por tanto, en el caso de los vehículos que cambian de dirección en la vía, no puede informar al maquinista de la indicación «¡Alto!». 


## Página 16

## 4.2.3 
### Visibilidad de la señal 
Figura 5: Visibilidad de la señal K4 desde el lugar de la autorización 
Desde el lugar ocupado por el agente de tráfico exterior (el extremo del tren), la indicación de la señal de salida es de visibilidad limitada debido a la placa de información al pasajero (Figura 5). Para una observación exacta, hay que caminar hacia adelante por el andén, o bajar la altura de los ojos, lo que requiere agacharse. En la grabación de la cámara instalada en el andén se ve claramente que el agente observó intencionadamente la señal de salida, inclinándose hacia adelante en lugar de mantener una postura vertical (Figura 6). 
Para el maquinista, la imagen indicativa de la señal de salida es perfectamente perceptible incluso en condiciones de visibilidad limitada, debido a su proximidad (Figura 3). La falta de observación de la señal por parte del maquinista no puede, por tanto, justificarse por una dificultad de percepción. 


## Página 17

### 4.3 
### Factores humanos 
## 4.3.1 
### Características humanas e individuales 
## 4.3.1.1 
### Maquinista 
El maquinista dispone de licencia de conducción de trenes de viajeros desde enero de 2018, y realiza habitualmente trenes en la línea ferroviaria n.º 80. El suceso se produjo en la segunda hora de su servicio de ese día; su servicio anterior había finalizado a las 16 horas 30 minutos del día anterior, por lo que el tiempo de descanso reglamentario le estaba garantizado. 
Llegó a la vía IV de la estación con el tren de viajeros de la relación Budapest-Keleti – Gödöllő a las 10 horas 44 minutos y, tras un cambio de cabina de conducción, en la hora de salida according al horario, según sus declaraciones creyó ver en el espejo retrovisor una autorización por parte del agente de tráfico exterior; a continuación, los revisores también subieron al tren, de lo que dedujo erróneamente que se cumplían las condiciones para la salida del tren. Sin observar la señal, puso el tren en marcha y, cambiando el desvío n.º 22, salió por la vía izquierda. A pesar de la indicación «- - -» visible en el indicador de la cabina de conducción, no le surgió ninguna sospecha sobre si realmente podía poner el tren en marcha. La Vb no logró averiguar la causa exacta de la falta de observación de las indicaciones. 
Según la observación in situ de la Vb, desde el espejo retrovisor del automotor es perceptible con la diligencia exigible al agente de tráfico que está realizando la autorización a 150 metros, en el extremo del tren, y los movimientos e indicaciones del revisor jefe situado en la primera puerta del tren son claramente identificables. 
## 4.3.1.2 
### Agente de tráfico encargado 
Tras establecer el itinerario de entrada del tren n.º 3114, el agente de tráfico abandonó la oficina de tráfico por motivos de salud durante los pocos minutos disponibles. 
Tras el tren, los desvíos desviaron desde la vía derecha hacia la vía III. Hasta la hora de salida according al horario del tren n.º 3135 quedaban entonces aún unos 5 minutos, por lo que no estableció su itinerario de salida. Regresó a la oficina cuando el tren partió de la vía IV con exactitud de segundos en la hora de salida according al horario; esto era visible en la interfaz de usuario del aparato de enclavamiento, por lo que, mediante el establecimiento de los desvíos situados ante el tren que iniciaba la salida, desvió el tren hacia la vía izquierda, correcta, y a continuación llamó por teléfono al maquinista para informarle de que podía circular hasta la estación de Isaszeg. 
El cambio de los desvíos ante el tren en marcha habría estado justificado en el caso de que el tren hubiera puesto en peligro otro movimiento; en la presente situación, esta circunstancia no concurría. En una situación de peligro, el desvío en una dirección segura del convoy que circula sin autorización puede estar justificado incluso a costa de que el desvío, que eventualmente cambia entre las ruedas en función de la velocidad del tren, pueda provocar el descarrilamiento del vehículo. 
La continuación de la circulación del tren por la vía izquierda, correcta, no conllevaba un riesgo de seguridad directo, ya que el tren tenía autorización hasta la estación de Isaszeg. Sin embargo, la autorización de la continuación de la circulación del tren detenido por el suceso extraordinario no compete ni al agente de tráfico ni al competencias del director de línea; a pesar de ello, modificaron el lugar del accidente.

## Página 18

## 4.3.2 
### Factores relacionados con el puesto de trabajo 
## 4.3.2.1 
### El proceso de autorización 
A partir de las grabaciones de las cámaras de vigilancia del andén, es posible reconstruir la actividad del agente de circulación exterior y de los revisores. 
Debido a la entrega de una orden escrita para el tren que llegaba a la vía III, el agente de circulación exterior se dirigió al andén en el momento de su llegada. Permaneció en el andén durante los aproximadamente 4 minutos entre la llegada del tren a la vía III y la salida del tren de la vía IV. 
Al acercarse la hora de salida según horario (11:16), se acaminó más cerca del extremo del tren y, aunque aún no había recibido instrucción de la autoridad competente sobre la autorización, se agachó para observar la señal de salida. Mientras tanto, durante unos 2 segundos, mantuvo el lado emisor de la señal del aparato de señalización de arranque de tren que tenía en la mano en posición horizontal delante de su cuerpo (figura 6). A continuación, incorporándose, giró el lado emisor de la señal del aparato hacia su cuerpo (figura 7). 
Esta secuencia de movimientos resultó ser, involuntariamente, apta para iniciar los distintos procesos de emisión de señales que preceden directamente al arranque del tren, ya que los revisores, tras emitir la señal «Listo para la salida» en ese momento, subieron al tren. Después, el agente de circulación exterior se agachó de nuevo varias veces para observar la señal de salida y, tras permanecer el tren todavía 20 segundos en posición detenida, este partió. Cuando el tren se puso en marcha, el agente de circulación exterior, situado en el extremo del tren, emitió con el aparato de señalización que tenía en la mano la señal «¡Alto!» hacia el maquinista, pero esta resultó ineficaz y el tren no se detuvo. 
Al comienzo del proceso mencionado —en la hora de salida según horario—, los revisores estaban situados en la primera y la última puerta del tren, esperando la señal «Llamada» del agente de circulación exterior. Dado que un movimiento muy similar a la señal era visible durante unos segundos por parte del agente de circulación exterior —aunque no intencionadamente y de forma irregular— (figura 6), los revisores pudieron interpretarlo erróneamente como tal, y dado que no había impedimento para la salida del tren desde el punto de vista de los revisores, ambos pudieron emitir la señal «Listo para la salida» (figura 7) antes de subir al tren. 
Sin embargo, no se cumplían todas las condiciones de circulación para la salida del tren —no había señal que autorizara la continuación de la marcha en la señal de salida—, por lo que el agente de circulación exterior no emitió la señal «Llamada para la salida». 
Para el maquinista, el significado de la señal «Listo para la salida» de los revisores y de la información transmitida por su subida al tren depende del lugar de servicio en que se produce y de a quién (al maquinista o al agente de circulación) se dirige la señal: 
- En las paradas y en aquellos lugares de servicio en los que el revisor jefe autoriza a los maquinistas del tren para la salida, la secuencia de acciones anterior —junto con la imagen de señal que autoriza la continuación de la marcha de la señal— es la condición necesaria y suficiente para la salida; 
- En las estaciones en las que la autorización la realiza el agente de circulación con el aparato de señalización de arranque de tren, esta es también una condición necesaria pero no suficiente para la puesta en marcha del tren, además de lo enumerado en el punto anterior, la señal «Llamada para la salida». 
El maquinista se conformó con la señal «Listo para la salida» detectada en la hora de salida y con el hecho de que los revisores subieran al tren, y no prestó la debida atención a la ausencia de la señal del agente de circulación exterior, más difícil de reconocer en el espejo. 


## Página 19

La última posibilidad de evitar el suceso por parte del maquinista habría sido observar la señal, ya que su visibilidad no se veía obstruida (véase: 4.2.3). 
Figura 6: Los revisores y el agente de circulación a las 11:15:38, momento en el que el movimiento involuntario del agente de circulación exterior podía interpretarse como la señal «Llamada» 
Figura 7: A las 11:15:40 el agente de circulación exterior finalizó su secuencia de movimientos susceptible de malinterpretación, pero el revisor situado en el extremo del tren ya había emitido la señal «Listo para la salida» 
## 4.3.3 
### Factores ambientales 
La precipitación intensa en el momento de producirse el suceso no obstaculizó la observación de las señales y avisos, pero pudo influir en las acciones del agente de circulación exterior y de los revisores, en el sentido de que, por ello, todos pudieron esperar impacientes la salida del tren. 


## Página 20

## 4.3.4 
### Las señales como comunicación crítica para la seguridad 
Durante la explotación ferroviaria, el personal se comunica entre sí de diversas maneras. Esta comunicación puede materializarse, en presencia mutua, como comunicación verbal personal, mediante el uso de un medio técnico de forma oral (teléfono, radio), por escrito y mediante señales. 
En la comunicación crítica para la seguridad, es un requisito fundamental transmitir la información redactándola con precisión y excluyendo la posibilidad de error. En caso de que surja alguna duda sobre cualquier elemento de la comunicación, existe la posibilidad de solicitar una aclaración. En la comunicación oral, el personal tiende a usar simplificaciones y jerga. 
En la comunicación realizada mediante señales no existe la posibilidad de esta aclaración, por lo que, ante una señal dudosa, no debe ejecutarse. No obstante, también en la comunicación mediante señales se debe procurar que el personal emita las señales de forma inequívoca y que no actúe de manera intencionada ni accidental de forma que resulte engañosa para quien observa la señal. 
En este caso, el agente de circulación exterior emitió involuntariamente una señal que, aunque fue visible durante un breve período de tiempo, correspondía a una señal recogida en una instrucción, y, al verla, el personal realizó de forma rutinaria todo el proceso de salida. El agente de circulación exterior no emitió esta señal conforme a una instrucción, pero, de manera similar a la jerga utilizada en la comunicación oral, la señal podía entenderse como una señal emitida con un movimiento descuidado y poco preciso, cuya emisión de este modo es general y generalmente aceptada en la red ferroviaria. 
### 4.4 
### Sucesos similares anteriores 
## 4.4.1 
### 28 de julio de 2018, Tatabánya (2018-0904-5) 
El tren n.º 34494, autorizado por el agente de circulación exterior desde la estación de Tatabánya, pasó junto a la señal de salida individual V5a con la señal «¡Alto!», cortó el desvío n.º 17/a y circuló hasta la estación de Környe. 
Durante la investigación, el Vb determinó que el aparato de enclavamiento funcionaba con normalidad y que no apareció imagen de señal que autorizara la continuación de la marcha en la señal de salida ni en la señal de la cabina de conducción. Como causa indirecta del suceso, la investigación reveló que —de forma similar a este suceso—, debido a la construcción del aparato de enclavamiento, en los trenes que cambian de sentido en la vía V/a, la alimentación del paso 1 para el control de tren solo se produce desde la dirección de la señal V5a después de la establecimiento de la vía, por lo que no garantiza la función de detención del tren para el tren que llega a la vía muerta y regresa desde ella. 
## 4.4.2 
### 15 de marzo de 2020, Vác (2020-0283-5) 
En la estación de Vác, para el tren n.º 32228 que partía de la vía III.b, se estableció erróneamente la vía de salida desde la vía IV.b; a continuación, el agente de circulación exterior autorizó al maquinista para la salida, quien puso en marcha el tren y, sin autorización, rebasó la señal de salida individual V3a con la señal «¡Alto!», cortó el desvío n.º 19 y, finalmente, el tren se detuvo en el desvío n.º 17, que también estaba establecido incorrectamente para él. 
El Vb identificó como factores que contribuyeron al suceso que la emisión de señales no funciona, en el caso del tren que llega a la estación y vuelve a salir después del cambio de sentido, hasta que se produce el establecimiento de la vía desde la vía correspondiente, por lo que el aparato de control de tren no emitió una llamada de alerta comprimida al maquinista, que habría ayudado a reconocer la situación; además, tampoco se produjo el frenado de emergencia al pasar junto a la señal con la señal «¡Alto!». 


## Página 21

### 5. 
### CONCLUSIONES 
### 5.1 
### Resumen 
## 5.1.1 
### Factores de causa-efecto 
Acciones, errores, sucesos o condiciones, o combinaciones de los mismos, cuya corrección, eliminación o evitación habría hecho posible, con toda probabilidad, prevenir la ocurrencia del accidente o del suceso inesperado: 
a) El maquinista partió con el tren sin autorización y en ausencia de una señal que autorizara la continuación de la marcha en la señal de salida (4.3.1.1). 
## 5.1.2 
### Factores contribuyentes 
Acciones, errores, sucesos o condiciones que influyeron en el suceso al aumentar la probabilidad de ocurrencia, acelerar los efectos o agravar la gravedad de las consecuencias, pero cuya eliminación no habría impedido la ocurrencia del suceso: 
a) La emisión de señales no funciona para el tren saliente después del cambio de sentido hasta que se produce el establecimiento de la vía desde la vía correspondiente, por lo que tampoco se produce el frenado de emergencia al pasar junto a la señal con la señal «¡Alto!» (4.2.2); 
b) Los movimientos involuntarios del agente de circulación exterior se asemejaron durante un breve período a la señal «Llamada» (4.3.2.1); 
c) El personal revisor interpretó los movimientos involuntarios del agente de circulación como la señal «Llamada» (4.3.2.1). 
## 5.1.3 
### Factor de nivel sistémico 
El Vb no identificó factores de causa-efecto o contribuyentes de carácter organizativo, directivo, social o normativo que probablemente puedan tener efecto en el futuro sobre sucesos similares y relacionados. 
### 5.2 
### Observaciones adicionales 
El Vb no identificó factores que aumenten el riesgo y que no puedan relacionarse con la ocurrencia del caso. 
### 5.3 
### Lecciones aprendidas 
El caso sirve de lección sobre una de las deficiencias de construcción del sistema existente de emisión continua de señales, ya que la dirección de marcha del vehículo y la dirección de alimentación de las señales de vía deben ser opuestas para un funcionamiento correcto. Sin embargo, al cambiar la dirección de marcha de los trenes, la dirección de alimentación no se invierte; para ello se requiere una acción activa por parte del operador del aparato de enclavamiento, independiente del maquinista. Durante el tiempo en que esto no se produce, el aparato de control de tren funciona como si se encontrara en un tramo de vía no dotado de emisión de señales, y los maquinistas deben circular con conocimiento de ello. Por tanto, en este momento el papel del dispositivo de protección automática debe ser asumido por el ser humano, y la eliminación de las fuentes de peligro inherentes a ello es posible mediante una atención consciente y reforzada. 
El suceso sirve también de lección sobre el hecho de que una señal manual no emitida intencionadamente conlleva un riesgo crítico para la seguridad. 


## Página 22


## Página 23

### ANEXOS 
Los datos fácticos que tuvieron una influencia esencial en el suceso y/o en su investigación, y que no se han expuesto de otra forma en el informe final. 
Anexo 1 
### El registrador de datos del vehículo ferroviario

## Página 24

2. Anexo
### Las normas, instrucciones y órdenes de servicio citadas
### La autorización al maquinista para la salida la regula la Instrucción de Circulación F.2:
### Reglas básicas de la autorización: 15.17.2. La autorización solo puede concederse después de haber adoptado todas las medidas de seguridad necesarias para la circulación del tren. Puede conceder la autorización:
a) el agente de circulación mediante señales de vía,
b) el agente de circulación con gorra roja:
— con el aparato de señal de salida de tren,
— con señal previa y aparato de señal de salida de tren,
(…)
## 15.17.2.1.
(…) Para autorizar al maquinista a la salida o al paso, con el aparato de señal de salida de tren, hay que situarse junto al tren en un lugar desde el que el maquinista pueda ver al empleado que realiza la autorización y la señal Llamada a la salida. El punto más lejano para la autorización es el furgón de señal.
### Actuaciones del maquinista: 15.17.4. El maquinista solo podrá hacer salir su tren o pasar si ha sido autorizado para ello. El maquinista no puede hacer salir trenes de viajeros antes de la hora de salida prevista en el horario.
### 15.17.4.1. Antes de la salida del tren, el maquinista está obligado a comprobar personalmente que su tren ha sido autorizado para la salida y que la señal de los señales fijos que autoriza la continuación de la marcha se refiere a su tren.
Para comprobar la autorización, si es necesario, debe cruzar al lado de la vía donde se realiza la autorización. Después de la autorización, si el maquinista no puede comprobar la posición de autorización de continuación de la marcha del señal fijo, debe avanzar con precaución lo suficiente para poder comprobar la posición de la señal de salida.
## 15.17.5.2.
Al autorizar al maquinista de un tren que circula con varios acompañantes del tren, hacia los acompañantes del tren — y si es necesario también hacia la delantera y la trasera del tren — debe darse la señal Llamada y, si es necesario, simultáneamente la señal ¡Acompañantes a sus puestos!
Si el(los) revisor(es) está(n) listo(s) para la salida, deben dar la señal Listo para la salida hacia el revisor jefe; si no están listos, deben dar la señal ¡Alto!
Si el revisor jefe da la señal Listo para la salida al empleado que realiza la autorización, el agente de circulación está obligado a dar la señal Llamada a la salida hacia el maquinista.
Si algún acompañante del tren da la señal ¡Alto! o no da la señal Listo para la salida, después de eliminar el obstáculo debe repetirse la señal Llamada.
El revisor jefe debe tener cuidado de dar la señal Listo para la salida hacia el autorizador solo cuando todos los acompañantes del tren hayan dado también esta señal.
El revisor jefe debe situarse en todo caso en un lugar desde el que pueda comprobar la señal dada por el(los) revisor(es).


## Página 25

### Señales dadas por el agente de circulación antes de la salida del tren (F.1.
### Instrucción de Señalización)
### 6.1.1.1. Llamada.
El empleado que realiza la autorización sostiene el aparato de señal de salida de tren, de día con su cara verde, de noche con su luz verde, a la altura del hombro, inmóvil, orientado hacia los acompañantes del tren.
### 6.1.1.4. Llamada a la salida.
El empleado que realiza la autorización, con el cuerpo orientado hacia el tren y el rostro hacia el maquinista del tren, mueve el aparato de señal de salida de tren, de día con su cara verde, de noche con su luz verde, orientado hacia el maquinista, en dirección vertical hacia arriba y hacia abajo.
Las imágenes de señal de la señal de cabina de conducción deben interpretarse conforme a las de la F.1. Instrucción de Señalización.
### 3.2.6. No llega la señal evaluable desde la vía.
### (…) En la señal de cabina de conducción ETCS, tres líneas horizontales negras sobre fondo blanco.
El equipo es inutilizable, o el tren ha pasado de un tramo de vía no equipado para el control del tren a un tramo equipado para el control del tren pero ocupado, o el tren ha llegado a un tramo de vía que no está equipado para el control del tren.
### 3.2.1. En el siguiente señal hay una señal que autoriza la continuación de la marcha sin reducción de velocidad.
### (…) En la señal de cabina de conducción ETCS, la inscripción negra MAX sobre fondo verde.
### 3.2.4. En el siguiente señal hay la señal ¡Alto! Prepararse para detenerse.
### (…) En la señal de cabina de conducción ETCS, la indicación del número 0 (cero) negro sobre fondo amarillo.
