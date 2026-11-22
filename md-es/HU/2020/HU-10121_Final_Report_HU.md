---
pais: HU
anio: 2020
idioma_origen: HU
md_origen: md/HU/2020/HU-10121_Final_Report_HU.md
md5_origen: 96cc34f07678193b32feea1900957669
modelo: mimo-v2.6-flash
bloques: 3
chars: 39831
ratio_longitud: 1.15
tokens_in: 17856
tokens_out: 12164
verificacion: revisar
fecha_proceso: 2026-11-22
generador: traducir_md_es.py (traducción IA + verificación numérica)
avisos: ["página 7: cifras largas: faltan 1/4 (25%)"]
notas_cifras: ["página 5: original bilingüe: se compara contra el idioma principal (HU)", "página 6: original bilingüe: se compara contra el idioma principal (HU)", "página 10: original bilingüe: se compara contra el idioma principal (HU)", "página 11: original bilingüe: se compara contra el idioma principal (HU)", "página 12: original bilingüe: se compara contra el idioma principal (CS)", "página 16: original bilingüe: se compara contra el idioma principal (HU)"]
---
## Página 1

MINISTERIO DE TECNOLOGÍA E INDUSTRIA 
ORGANISMO DE SEGURIDAD DEL TRANSPORTE 
INFORME FINAL 
2021-0861-5 
(HU-10121) 
Incidente ferroviario imprevisto / Paso de señal 
Győr, 25 de agosto de 2021 


## Página 2

### Principios de la investigación técnica 
El objetivo de la investigación técnica es el esclarecimiento de las causas y circunstancias de los accidentes ferroviarios graves, de los accidentes ferroviarios y de los incidentes ferroviarios imprevistos, así como la iniciación de las medidas técnicas necesarias para la prevención de casos similares y la formulación de propuestas. La investigación técnica no tiene como objetivo, en ninguna forma, la investigación y determinación de la culpabilidad o de la responsabilidad. 
Las conclusiones de la investigación se basan en la evaluación por parte del OSGT de las pruebas disponibles y obtenidas durante la misma, teniendo en cuenta los principios de un procedimiento justo e imparcial. El informe final solo nombra a las personas implicadas en el accidente en función del puesto de trabajo y las funciones que desempeñaban en el momento del incidente. 
El OSGT está obligado a conservar y no está obligado a hacer accesible a otra autoridad los datos de los que tenga conocimiento durante la investigación técnica, respecto de los cuales el titular de los datos podría haber denegado la comunicación de datos en virtud de la legislación.1 
El Informe Final no tiene fuerza vinculante y contra él no puede iniciarse ningún procedimiento de recurso. 
El Organismo de Seguridad del Transporte llevó a cabo la investigación 
- 
con arreglo a la Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de navegación interior y de otros incidentes de transporte (en adelante: Ley Kbvt.); 
- 
con arreglo al Reglamento de Ejecución (UE) 2020/572 de la Comisión (24 de abril de 2020) sobre la estructura de los informes que deben seguirse en los informes de investigación de accidentes ferroviarios e incidentes imprevistos; 
- 
con arreglo al Reglamento NFM 24/2012 (V.8.) sobre las normas detalladas de la investigación técnica de los accidentes ferroviarios graves, de los accidentes ferroviarios y de los incidentes ferroviarios imprevistos, así como de la investigación del titular de la explotación; 
- 
y, en defecto de disposiciones distintas de la Ley Kbvt., aplicando adecuadamente las disposiciones de la Ley CL de 2016 sobre el procedimiento administrativo general. 
La Ley Kbvt. y el Reglamento NFM 24/2012 (V.8.) sirven conjuntamente para el cumplimiento del acto jurídico de la Unión constituido por la Directiva (UE) 2016/798 del Parlamento Europeo y del Consejo, de 11 de mayo de 2016, relativa a la seguridad ferroviaria (en adelante: Directiva de seguridad ferroviaria). 
La competencia del Organismo de Seguridad del Transporte se basa en el Decreto Gubernamental 230/2016 (VII. 29.) sobre el designación del organismo de seguridad del transporte y sobre la extinción del Organismo de Seguridad del Transporte con sucesión universal. 
La investigación técnica es independiente de las demás actuaciones administrativas, de infracción o penales iniciadas en relación con el accidente de transporte u otros incidentes de transporte. 
### Derechos de autor 
El informe final fue emitido por: 
### Ministerio de Tecnología e Industria, Organismo de Seguridad del Transporte 
1103 Budapest, Kőér u. 2/A. 
www.kbsz.hu 
kbszvasut@tim.gov.hu 
El informe final o sus partes pueden utilizarse en cualquier forma, teniendo en cuenta las excepciones establecidas por la legislación, siempre que los detalles conserven su contexto de contenido y se indique correctamente la fuente. 
1en virtud de los apartados 18.º (1) y (6) de la Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de navegación interior y de otros incidentes de transporte 


## Página 3

## DEFINICIONES Y ABREVIATURAS 
DGP 
Procesador de Diagnóstico del Aparato de Enclavamiento de la estación 
DVJ 
Señal de Cabina Digital. La función del dispositivo es la repetición de la imagen de señalización de la señal próxima en la cabina de conducción de la locomotora, en vía equipada con transmisión de señales. 
ERAIL 
Base de datos de accidentes de la Agencia Ferroviaria de la Unión Europea 
ETCS 
sistema europeo unificado de control de trenes (European Train Control System) 
EVM 
Aparato Electrónico de Parada de Tren 
Floyd Zrt. 
Floyd Szolgáltató Zrt. 
transmisión de señales 
función de transmisión de datos incorporada a la vía ferroviaria, que transmite a la cabina de conducción la información relativa a la imagen de señalización de la señal próxima 
paso de señal 
en el uso de términos de este informe final, significa un suceso en el que un tren pasa sin autorización junto a una señal principal en posición «¡Alto!» 
KBSZ 
Organismo de Seguridad del Transporte del Ministerio de Tecnología e Industria 
Kbvt. 
Ley CLXXXIV de 2005 sobre la investigación técnica de los accidentes de aviación, ferroviarios y de navegación interior y de otros incidentes de transporte 
MÁV Zrt. 
Magyar Államvasutak Zrt. 
MÁV-Start Zrt. 
MÁV - START Vasúti Személyszállító Zrt 
MFB 
Aparato de a Bordo de Locomotora (aparato que desempeña funciones de seguimiento de tren, registro de datos y licencia electrónica de conducción) 
TIM VHF   
Departamento Principal Ferroviario de Autoridades del Ministerio de Tecnología e Industria. 
VNN-EVM 
Registrador electrónico de datos. 
psz. 
número de vehículo 
Vb 
Comisión de Investigación 


## Página 4

CONTENIDO 
1. 
RESUMEN 
5 
2. 
EL PROCESO DE INVESTIGACIÓN Y SUS RELACIONES 
6 
2.1
Inicio de la investigación 
6 
2.2
Motivo del inicio de la investigación 
6 
2.3
Alcance y limitaciones de la investigación 
6 
2.4
La Comisión de Investigación 
6 
2.5
Procesos de comunicación y consulta 
7 
2.6
Colaboración 
7 
2.7
Métodos de investigación 
7 
2.8
Dificultades de la investigación 
7 
2.9
Contacto con las autoridades judiciales 
7 
3. 
DESCRIPCIÓN DEL SUCESO 
8 
3.1
Descripción del suceso 
8 
3.2
Cronología del suceso 
12 
4. 
ANÁLISIS DEL SUCESO 
14 
4.1
Funciones de las personas y organizaciones 
14 
4.2
Los vehículos y los aparatos técnicos 
14 
4.3
Factores humanos 
15 
4.4
Sucesos similares anteriores 
16 
5. 
CONCLUSIONES 
17 
5.1
Resumen 
17 
5.2
Medidas adoptadas 
17 
5.3
Observaciones adicionales 
17 
5.4
Procedimientos y prácticas que funcionan bien 
17 
5.5
Lecciones aprendidas 
17 
6. 
RECOMENDACIÓN DE SEGURIDAD 
18 
7. 
OPINIONES DISCREPANTES 
18 
ANEXOS 
19 


## Página 5

## 1. 
## RESUMEN 
El 25 de agosto de 2021, en la estación de Győr, el tren de mercancías n.º 44284-1 pasó sin autorización a las 9 horas 47 minutos la señal «V2» de salida que indicaba «¡Alto!». El tren fue frenado por el sistema de control de trenes y finalmente se detuvo a 400 metros después de la señal. 
Como consecuencia del paso de señal, el tren entró en el itinerario dispuesto hacia la vía derecha, en dirección a la estación de Öttevény, para el tren de pasajeros n.º 9442, que partió de la vía VI de la estación tras obtener autorización, tras cortar el desvío n.º 5. El maquinista del tren de pasajeros, al percibir el peligro, detuvo su tren con frenado brusco antes del último desvío n.º 9, que desvía hacia la vía derecha. 
En el suceso no se produjeron lesiones personales. 
Durante la investigación, la CI determinó que el maquinista del tren de mercancías no tuvo en cuenta la señalización de la señal de entrada que daba preaviso de la señal de salida «V2» (una luz amarilla), no comenzó a reducir la velocidad de su tren y, por lo tanto, pasó junto a la señal de salida en posición «¡Alto!» a una velocidad de 74 km/h. 
En el tramo posterior a la señal de entrada, de acuerdo con la corriente de señalización aplicada, apareció el número «0» en la señal de la cabina de conducción y, como efecto del cambio de señal, la bocina de vigilancia emitió una llamada. El maquinista la atendió, pero no redujo la velocidad de su tren. Además, el aparato EVM emitió otras dos llamadas de vigilancia (comprimidas), de las cuales no atendió la segunda – es decir, en total la tercera – llamada. Ante la falta de atención, el aparato EVM ejecutó un frenado de emergencia y, como efecto de ello, se detuvo el tren. 
El OSGT no emite una recomendación de seguridad, ya que, de haberse cumplido las normas relativas a la observación de las señales, el incidente ferroviario imprevisto se habría podido evitar. 


## Página 6

## 2. 
## EL PROCESO DE INVESTIGACIÓN Y SUS RELACIONES 
## 2.1
### Inicio de la investigación 
El caso fue comunicado a la guardia del OSGT por el Director de Control de Red de MÁV Zrt. el 25 de agosto de 2021, a las 10 horas (13 minutos después de la ocurrencia). 
El responsable de guardia del OSGT ordenó una inspección inmediata en el lugar. En función de las observaciones de la inspección, el responsable del OSGT decidió iniciar una investigación técnica. 
## 2.2
### Motivo del inicio de la investigación 
El Organismo de Seguridad del Transporte, con arreglo al apartado 7.º (1) de la Ley Kbvt., 
1. investiga los accidentes ferroviarios graves; 
2. puede investigar aquellos accidentes ferroviarios e incidentes ferroviarios imprevistos que, a su juicio, en circunstancias ligeramente distintas podrían haber conducido a accidentes graves, valorando 
a) la gravedad del accidente o del incidente ferroviario imprevisto, 
b) si forma parte de una serie de sucesos de importancia desde el punto de vista del sistema en su conjunto, 
c) 
el efecto sobre la seguridad ferroviaria, 
d) las solicitudes de los operadores de la red de vías, de las empresas ferroviarias, de las autoridades nacionales de seguridad o de los Estados miembros; 
e) si la investigación puede aportar lecciones en materia de seguridad. 
La presente investigación se inició con arreglo al punto b) del apartado (2) anterior (también en consonancia con el artículo 20.º (2) a) de la Directiva de seguridad ferroviaria (UE) 2016/798), porque durante el suceso, aunque no se produjo ninguna colisión ni lesiones personales, los pasos de señal sin autorización conllevan un riesgo muy alto. 
La investigación y la extracción de lecciones permiten mitigar el riesgo de accidentes en el transporte ferroviario. 
## 2.3
### Alcance y limitaciones de la investigación 
El objetivo de la investigación fue el esclarecimiento cronológico del desarrollo del suceso, la identificación de los factores humanos y técnicos que influyeron en la actividad de las personas y en el funcionamiento de los aparatos técnicos, la determinación de las causas directas e indirectas y la presentación de las lecciones necesarias. 
La investigación se extendió a las características de funcionamiento del aparato de control de trenes. 
## 2.4
### La Comisión de Investigación 
El responsable del OSGT designó la siguiente Comisión de Investigación para la investigación del suceso ferroviario: 
responsable 
Kapocsi József 
investigador de accidentes 
miembro 
Almási Bernát Gábor 
investigador de accidentes 
La CI disponía de las competencias necesarias para llevar a cabo la investigación, por lo que no fue necesario recurrir a expertos externos. 


## Página 7

### 2.5
### Procesos de comunicación y consulta 
La CI escuchó en el lugar al maquinista del tren n.º 44284-1, así como al maquinista del tren n.º 9442 y al responsable de tráfico de mando de la estación de Győr. 
### Proyecto de informe final 
El OSGT envió el proyecto de informe final a 
 
TIM VHF., 
 
MÁV Zrt., 
 
MÁV-Start Zrt., 
 
FLOYD Zrt. 
Al proyecto de informe final, por escrito, 
 
TIM VHF., 
 
MÁV Zrt., 
 
FLOYD Zrt. 
no formularon observaciones. 
## 2.6
### Colaboración 
MÁV Zrt., como operador de la red de vías, así como MÁV-Start Zrt. y FLOYD Zrt., que explotaban los trenes implicados, garantizaron durante todo el proceso de investigación el acceso a los datos solicitados por la CI. 
## 2.7
### Métodos de investigación 
Para la investigación, la CI utilizó 
- 
las observaciones de la inspección en el lugar realizada el 25 de agosto de 2021; 
- 
los datos de marcha extraídos del registrador de datos de la locomotora del tren de mercancías n.º 44284-1 (Anexo 1); 
- 
los datos MFB del tren de pasajeros n.º 9422; 
- 
la descripción técnica del aparato de enclavamiento de la estación de Győr; 
- 
la lista simplificada de sucesos del aparato de enclavamiento (Anexo 2); 
- 
las audiciones mencionadas también en el capítulo 2.5. 
Durante la investigación se realizaron pruebas: la CI, en el marco de una prueba en marcha con la locomotora del tren de mercancías n.º 44284-1, examinó las señales que aparecían en el DVJ y el 
### funcionamiento del aparato de control de trenes. La prueba se realizó desde la parada Győr – Gyárváros hasta la vía 2 de la estación de Győr, durante la cual el responsable de tráfico de mando situó las señales principales de la estación en la posición que tenían en el momento del suceso (Anexo 3). 
## 2.8
### Dificultades de la investigación 
La CI no se enfrentó a ninguna tarea que supusiera una dificultad especial durante la investigación. 
## 2.9
### Contacto con las autoridades judiciales 
La 
CI 
colaboró 
en 
el 
lugar 
con 
los 
empleados 
del 
Departamento 
de 
Policía 
de 
Tráfico 
de 
la 
Comisaría 
de 
Policía 
de 
Győr 
que 
realizaban 
la 
inspección 
en 
el 
lugar.

## Página 8

## 3. 
## DESCRIPCIÓN DEL SUCESO 
## 3.1
### Descripción del suceso
El 25 de agosto de 2021, a las 9 horas 47 minutos, el tren de mercancías n.º 44284-1, en la vía principal de paso de la estación de Győr, superó sin autorización la señal de salida individual n.º «V2» que indicaba «¡Alto!», y a continuación, al pasar por la aguja n.º 5, entró en la itinerario establecido hacia la vía derecha, en dirección a la estación de Öttevény, para el tren de viajeros n.º 9442 que partía autorizado desde la vía VI de la estación. El maquinista del tren de viajeros, al percibir el peligro, detuvo su tren con frenado de emergencia antes de la aguja n.º 9, última que desvía hacia la vía derecha. No hubo lesiones personales.
## 3.1.1 
### Tipo de suceso
Tipo de suceso: 
### Suceso ferroviario inesperado
Naturaleza del suceso: 
### Paso de señal
## 3.1.2 
### Fecha y lugar del suceso
Fecha del suceso: 
25 de agosto de 2021, 9 horas 47 minutos 
Lugar: 
red nacional de vías férreas
### Línea ferroviaria n.º 1 (Budapest-Keleti – Hegyeshalom oh.) 
### Estación de Győr
### Figura 1: Lugar del suceso (mapa: openrailwaymap.org)
## 3.1.3 
### Lugar del suceso
La estación de Győr es la estación intermedia de la línea ferroviaria n.º 1 Budapest - Hegyeshalom - Rajka. Es una estación de bifurcación hacia las líneas n.º 10 (Győr – Pápa – Celldömölk) y n.º 11 (Győr – Veszprém), así como estación de enlace de la línea ferroviaria n.º 8 (Győr – Sopron; GySEV Zrt.). A la estación pertenece también el patio de maniobras de 


## Página 9

Győr–Rendező, que gestiona un tráfico también significativo. La estación de viajeros de Győr dispone de 7 vías de recepción de trenes, a las que los pasajeros pueden acceder a través de dos pasos subterráneos. La entrada y salida de los pasajeros se facilita mediante andenes laterales.
Desde la dirección de llegada del tren de mercancías, después de la señal de salida n.º «V14b» de la estación Győr - Rendező —que es a la vez la señal de entrada de la estación de Győr—, la vía férrea gira hacia los andenes de la estación mediante un tramo curvado a la izquierda. Desde el final de la curva (a unos 630 metros de distancia) se hace visible la señal de salida individual n.º «V2», situada en el lado derecho de la vía. Hasta este punto, la visibilidad está limitada por la estructura de cubierta del andén de viajeros situado en el lado izquierdo de la vía.
En el momento de producirse el suceso, nuestro país se encontraba tras un frente frío. Predominaba un tiempo ventoso y despejado, con temperaturas en torno a los 20oC, y la visibilidad no estaba limitada.
Itinerario del tren de viajeros
### Figura 2: Detalle del croquis distorsionado de la estación de Győr, con los itinerarios utilizados en el momento del suceso
## 3.1.4 
### Consecuencias
### Lesiones personales
En el tren de mercancías n.º 44284-1 solo se encontraba el maquinista, y en el tren de viajeros n.º 9442, además del maquinista y del revisor jefe, se encontraban unos 30 pasajeros. No hubo lesiones personales.
### Daños materiales
Se produjeron daños materiales leves.
### Daños medioambientales
No se produjeron daños medioambientales.
## 3.1.5 
### Otras consecuencias
Como consecuencia del suceso, ambas vías de la línea principal n.º 1 quedaron excluidas del tráfico entre las estaciones de Győr y Öttevény. Después de que el tren de viajeros n.º 9442 fuera empujado de vuelta junto al andén, a partir de las 11 horas 47 minutos (2 horas después del suceso) pudo reanudarse el tráfico en la vía izquierda del tramo entre estaciones, pero debido a la ocupación aparente de la aguja n.º 9, los trenes circularon con señal de llamada en el extremo final de la estación. A las 14 horas 48 minutos, después de que el tren de mercancías fuera arrastrado de vuelta a la estación y de la inspección de la aguja n.º 5, 


## Página 10

la vía derecha también fue devuelta al tráfico sin restricciones.
Hasta las 14 horas 7 minutos (durante 4 horas 20 minutos), hasta que los 39 vagones del tren de mercancías fueron arrastrados de vuelta a Győr-Rendező, el convoy bloqueó el paso a nivel n.º SR5 —de la calle Újlak—, que une la zona de Győr Nádorváros con el centro de la ciudad.
## 3.1.6 
### Organizaciones y personas afectadas
El operador de la red nacional de vías férreas es MÁV Magyar Államvasutak Zrt., que dispone de autorización de explotación de la red nacional de vías férreas. El jefe de servicio de tráfico y los agentes de servicio de tráfico de la estación de Győr eran empleados de MÁV Zrt.
El tren de mercancías n.º 44284-1 era operado por Floyd Zrt., que dispone de autorización nacional de transporte de mercancías. El propietario de la locomotora del tren es Constantin Grup Srl de Rumanía.
El tren de viajeros n.º 9442 era operado por MÁV-Start Zrt., que dispone de autorización de transporte ferroviario de viajeros. El personal del tren pertenecía a la plantilla de MÁV-Start Zrt.
## 3.1.7 
### Los trenes
Se vieron implicados en el suceso: 
 
el tren de mercancías n.º 44284-1, circulando de Budaörs vía Rajka hasta Rusovce (SK), remolcado por la locomotora n.º de matrícula 91 53 040 1085-2: 
n.º de vagones: 
40 
longitud: 
583 m 
masa del tren: 
881 t 
 
el tren regional de viajeros n.º 9442, circulando de Győr vía Hegyeshalom hasta la estación de Bruck a.d. Leitha (A), remolcado por la unidad de tren automotor n.º de matrícula 94 55 1425 010-5: 
n.º de vagones: 
1 unidad de tren automotor 
longitud: 
67 m 
masa del tren: 
150 t 
## 3.1.8 
### La infraestructura
En la estación de Győr funciona un enclavamiento electrónico de itinerarios de maniobras THALES ELEKTRA 2, de centro único, con agujas de accionamiento eléctrico y señales luminosas, que comprueba continuamente la ocupación de las agujas y las vías. Todos los itinerarios se establecen a través de vías cerradas cubiertas por señales de maniobra y de tren. El enclavamiento de la estación gestiona y supervisa también la conexión con Győr-Gyárváros, así como con Győr-Rendező.
En la estación también funciona el control puntual de trenes ETCS nivel 1 y la emisión de señal programada en circuito de vía de 75 Hz. En los sectores de aguja, en los tramos independientes situados detrás de las señales de salida, la emisión de señal está garantizada por los cables emisores de 75 Hz.


## Página 11

### Dispositivo de parada de tren EVM-120
Funcionamiento del dispositivo en el tramo de vía no equipado para la transmisión de las imágenes de señal de las señales laterales: 
- 
en este tramo de vía solo funciona la función de control de vigilancia, 
- 
la condición de funcionamiento es que el dispositivo esté encendido y que la velocidad del vehículo sea superior a 15 km/h; en ese caso, el dispositivo solo realiza un control de vigilancia proporcional a la distancia recorrida. 
Funcionamiento del dispositivo en el tramo de vía apto para la transmisión de las imágenes de señal de las señales laterales: 
- 
que el dispositivo esté encendido, 
- 
en el tramo de vía equipado para la emisión de señal, se induce en la bobina receptora una tensión proporcional a las corrientes de señal, 
- 
estas señales inducidas no pueden procesarse directamente, por lo que dichas señales son convertidas por dispositivos de amplificador de filtro y decodificador, 
- 
la unidad de recepción de señal realiza la visualización en el indicador de la cabina de los señales de vía evaluadas /decodificadas/. 
La información transmitida mediante los pulsos proporciona una orden de velocidad al maquinista, en forma de imágenes de color y pictogramas mostrados en el indicador de la cabina: 
- 
pulso 0, el circuito de vía no recibe alimentación, o se emite una alimentación no codificada, 
- 
pulso 1, en la señal aproximada hay señal de «¡Alto!», 
- 
pulso 2, en la señal aproximada hay señal de vía libre reducida, que permite la circulación a una velocidad máxima de 40 km/h, 
- 
pulso 3, en la señal aproximada hay señal de vía libre reducida, que permite la circulación a una velocidad máxima de 80 km/h, 
- 
pulso 4: en la señal aproximada hay señal que permite la circulación sin reducción de velocidad, 
- 
pulso X: el circuito de vía recibe una señal cuadrada programada de 75 Hz, pero esta no tiene contenido de imagen de señal. 


## Página 12

## 3.2
### Cronología del suceso
Sobre la base de las pruebas recabadas, el desarrollo real del suceso puede reconstruirse de la siguiente manera: 
## 3.2.1 
### Hechos anteriores al suceso
## 06:15  
El maquinista del tren de mercancías inició su servicio en la estación de Budaörs, en la locomotora, con el relevo personal del tren de mercancías de llegada. 
## 07:32 
Partió con su tren desde la estación de Budaörs. 
### Situación de tráfico en la estación de Győr antes del suceso: 
El jefe de servicio de tráfico pretendía despachar el tren de viajeros n.º 9442 desde la vía VI de la estación hacia Öttevény por la vía derecha. 
Por ello, pretendían detener el tren de mercancías n.º 44284-1 en la vía II de la estación, a diferencia de lo previsto en el horario. 
Las marcas de tiempo de los datos objetivos utilizados para la investigación del suceso se sincronizaron con el reloj del enclavamiento, y la cronología del suceso se muestra en función de ello. 
## 09:43:52 
El agente de servicio de tráfico de la estación de Győr estableció el itinerario entre la señal de entrada V14b y la señal de salida V2 hacia la vía II para el tren de mercancías n.º 44284-1. 
## 09:43:56 
En el itinerario entre la señal de entrada V14b y la señal de salida V2 se emitió el pulso 1. 
## 09:44:02 
En el itinerario entre la señal de entrada «D» de Győr- Rendező y la señal de entrada V14b de la estación de Győr se emitió el pulso 4. 
## 09:45:44 
El agente de servicio de tráfico estableció el itinerario desde la señal «V6» hacia la vía derecha en dirección a Öttevény para el tren de viajeros n.º 9442. 
## 09:45:49 
El paso a nivel SR5 se cerró. 
## 09:45:56 
En la segunda señal de salida V2a apareció la luz verde. 
## 09:46:18 
En la señal de salida V6 apareció la luz amarillo-verde, como consecuencia de lo cual en la vía VI se emitió el pulso 2. 
## 3.2.2 
### Desarrollo del suceso
## 09:46:27 
El tren de mercancías pasó a 93 km/h junto a la señal de entrada V14b, que daba un preaviso con luz amarilla, en dirección a la señal de salida V2.  
A continuación, el dispositivo EVM emitió tres avisos de vigilancia (comprimidos). 
## 09:46:43 
El tren de viajeros n.º 9442 partió de la vía VI. 
## 09:46:56 
El tren de viajeros pasó junto a la señal de salida V6. 
## 09:47:02 
Tras el tercer aviso de vigilancia, el dispositivo EVM inició un frenado de emergencia en la locomotora del tren n.º 44284-1; la velocidad del tren era entonces de 91 km/h, como consecuencia de lo cual el tren comenzó a reducir la velocidad. 


## Página 13

## 09:47:16 
El tren, ya reduciendo la velocidad por efecto del frenado de emergencia, pasó junto a la señal de salida V2 que indicaba «¡Alto!» a una velocidad de 74 km/h. 
El jefe de servicio de tráfico instruyó a través de la radio de locomotora al maquinista del tren de viajeros que detuviera su tren de inmediato. 
## 09:47:27 
El maquinista del tren de viajeros percibió la situación de emergencia y frenó de inmediato. 
El maquinista percibió el tren de mercancías que se aproximaba por la vía derecha y que la aguja n.º 9 estaba dispuesta en la dirección de desvío que desvía hacia la vía derecha, por lo que frenó de emergencia sin demora. 
## 09:47:30 
El tren de mercancías entró en el tramo SR5b, con lo que se vio afectada la protección lateral del itinerario del tren de viajeros; al continuar, la aguja 5 quedó ocupada. 
## 09:47:34 
El tren de viajeros se detuvo antes de la aguja 9, que desvía hacia la vía derecha, en el punto kilométrico 1418+90. 
## 09:47:36 
El tren de mercancías pasó por la aguja n.º 5. 
## 09:47:39 
El tren de mercancías se detuvo a 400 metros después de la señal de salida V2. 
Según declaró el maquinista, «se oyó un gran escape de aire en la válvula neumática eléctrica bajo la mesa de conducción; quiso eliminarlo, por lo que después de detenerse apagó y encendió el dispositivo EVM», con lo que borró su señal roja. 
El dispositivo de control de tren frenó de emergencia, como consecuencia de lo cual la válvula EVM dejó escapar al exterior la presión de la conducción principal, y el maquinista oyó el efecto sonoro de ello. 
## 3.2.3 
### Hechos posteriores al suceso
El tren de mercancías y el tren de viajeros permanecieron detenidos hasta la llegada del Vb. El Vb registró la posición de parada del tren de viajeros y autorizó que fuera empujado de vuelta a la vía VI de la estación. A continuación, tras registrar la posición de parada del tren de mercancías y la situación de los mandos del dispositivo de freno y del dispositivo EVM, los vagones del convoy se apartaron hacia Győr - Rendező. Después de esto se llevó a cabo la prueba mencionada en el capítulo 2.7.

## Página 14

## 4. 
## ANÁLISIS DEL SUCESO 
## 4.1
### Funciones de las personas y organizaciones 
## 4.1.1 
### Los maquinistas 
La función del maquinista es observar las señales y, en función de ellas, conducir su tren. Debe frenar a tiempo antes de una señal en disposición ¡Alto! La velocidad de su tren debe regularla de acuerdo con las instrucciones y disposiciones vigentes. 
La actividad del maquinista del tren de mercancías no cumplió esta exigencia según lo detallado en el capítulo 4.3. 
El maquinista del tren de pasajeros condujo su tren con atención y de acuerdo con las exigencias según lo detallado en el capítulo 4.3. 
### 4.2
### Los vehículos y los equipos técnicos 
## 4.2.1 
### Registradores de datos 
El locomotor con número de matrícula 91 53 0401 085-2, que remolcaba el tren de mercancías número 44284-1, estaba equipado con un registrador de datos tipo VNN-EVM y un dispositivo de influencia en el tren EVM-120 T 2200. 
La automotriz con número de matrícula 94 55 1425 010-5, que remolcaba el tren de pasajeros número 9442, estaba equipada con un registrador de datos de circulación MFB y Deuta KWR6. 
El Vb tomó como hora de referencia los datos horarios registrados por el dispositivo de enclavamiento; el cronómetro MFB de la automotriz adelantaba 5 segundos en comparación con este. El reloj del registrador de datos del tren de mercancías adelantaba 51 segundos respecto al cronómetro del dispositivo de enclavamiento. Los datos de los registradores de datos pudieron ser evaluados. 
## 4.2.2 
### Los mandos del dispositivo de freno y del dispositivo EVM 
El Vb constató en la inspección en el lugar que en el locomotor del tren de mercancías número 44284-1, en la válvula EP situada bajo la mesa de conducción del dispositivo de vigilancia y de influencia en el tren, el precinto estaba roto (figura 3), y no se había realizado ninguna anotación al respecto en el diario de operaciones del locomotor. La palanca de mando de la válvula de desfogue del locomotor estaba atada en posición de desfogue a la válvula de freno auxiliar (figura 4), presumiblemente para no tener que manipularla en los desfogues debidos al cuidado de las ruedas del locomotor durante los frenados operativos. De este modo, el locomotor no pudo frenar tampoco en la situación de peligro, lo que provocó un aumento de la distancia de frenado y agravó la gravedad del suceso. La válvula de freno auxiliar estaba en posición de frenado, y la válvula de frenado del dispositivo de freno automático estaba en posición de carga-desfogue. 


## Página 15

Figura 3: precinto roto 
Figura 4: válvula de desfogue atada 
## 4.3
### Factores humanos 
### El maquinista del tren de mercancías 
El maquinista tenía el período de descanso reglamentario antes de su entrada en servicio. Para iniciar su servicio, viajó desde su domicilio en Budapest hasta la estación de Budaörs. Circula habitualmente por la línea ferroviaria 1 y contaba con 3 años de experiencia como conductor de vehículos. 
No prestó atención a la señal de la señal de entrada de la estación de Győr, la luz amarilla, no comenzó a reducir la velocidad de su tren y pasó a 74 km/h junto a la señal de salida V2. 
El dispositivo de influencia en el tren del locomotor adoptó el paso 1 en el tramo posterior a la señal de entrada, de acuerdo con la corriente de señal suministrada; apareció la señal «0» en el indicador de la cabina de conducción y, como consecuencia del cambio de señal, la bocina de vigilancia emitió un aviso. El maquinista lo desactivó, pero no redujo la velocidad de su tren. Además, el dispositivo EVM emitió otros dos avisos de vigilancia (comprimidos); el maquinista no desactivó el tercer aviso. Ante la falta de manipulación, el dispositivo EVM ejecutó un frenado de emergencia y, como consecuencia de ello, se detuvo el tren. 
Según el horario, el tren no se habría detenido en la estación de Győr; siendo consciente de ello, la serie de acciones del maquinista indicó que no se preparó para detenerse en la estación, a pesar de las señales que le estaban indicadas y que eran bien perceptibles. Aunque desactivó de forma mecánica el primer aviso de vigilancia comprimido y el segundo, a estos no les siguió ninguna otra acción que influyera en la velocidad del tren. Tampoco le generó dudas el tren de pasajeros que circulaba en paralelo. 
Cuando fue interrogado durante la inspección en el lugar, el maquinista no recordaba con exactitud el aspecto de la señal de la señal V14b. Según sus recuerdos, «seguro que no era una señal amarilla». 
En contradicción con lo expuesto, según los datos registrados del dispositivo de enclavamiento y del locomotor, en la señal había una luz amarilla y estaba indicado el paso 1 en el circuito de raíl de la vía II. 


## Página 16

### El maquinista del tren de pasajeros 
Como consecuencia del suceso se produjo un peligro directo para la vida, sin embargo el maquinista del tren de pasajeros reconoció la situación de peligro, detuvo su tren inmediatamente con frenado de emergencia y, con ello, impidió la colisión de los trenes. 
## 4.4
### Sucesos similares anteriores 
## 4.4.1 
### 18 de mayo de 2011, Újfehértó (2011-0215-5) 
El tren de mercancías número 45439/56500-1 partió sin autorización a las 20 horas 48 minutos de la vía número V de la estación de Újfehértó y sobrepasó la señal de salida «K5» que prohíbe la continuación de la marcha. El maquinista aplicó frenado de emergencia antes de la aguja número 12, la primera afectada, que estaba mal dispuesta para él, y se detuvo a 42 metros después de la señal de salida «K5», en la ruta de la vía del tren número 6018 que entraba en la vía principal de paso derecho número IV, sin cortar la aguja. 
El tren número 6018 se aproximaba hacia la estación de Újfehértó a una velocidad aproximada de 120 km/h, la autorizada para él, cuando observó que la luz verde que le estaba indicada previamente en la señal de entrada cambiaba a roja. Aplicó inmediatamente frenado de emergencia y, a continuación, los dos trenes se detuvieron uno frente al otro a una distancia de 236 m. 


## Página 17

## 5. 
## CONCLUSIONES 
## 5.1
### Resumen 
## 5.1.1 
### Factores causales 
Acciones, errores, sucesos o condiciones, o bien sus combinaciones, cuya corrección, eliminación o evitación habría permitido, con toda probabilidad, prevenir la ocurrencia del accidente o del suceso inesperado: 
a) el maquinista llegó a la estación con su tren sin prepararse para detenerse, 
b) la señal recibida en la señal de entrada, su significado, no le resultó consciente y intentó atravesar la estación de acuerdo con el horario. 
## 5.1.2 
### Factores contribuyentes 
Acciones, errores, sucesos o condiciones que influyeron en el suceso al aumentar la probabilidad de ocurrencia, acelerar los efectos o agravar la gravedad de las consecuencias, pero cuya eliminación no habría impedido la ocurrencia del suceso: 
a) la palanca de la válvula de desfogue estaba atada, por lo que no permitió al locomotor frenar tampoco durante el frenado de emergencia, lo que resultó en un aumento de la distancia de frenado (4.2.2). 
## 5.1.3 
### Factores de nivel sistémico 
El Vb no identificó factores causales o contribuyentes de carácter organizativo, directivo, social o normativo que probablemente puedan tener influencia en el futuro sobre sucesos similares y relacionados. 
## 5.2
### Medidas adoptadas 
La compañía ferroviaria no adoptó medidas relevantes para la seguridad. 
## 5.3
### Observaciones adicionales 
El Vb no identificó factores que aumenten el riesgo y que no puedan relacionarse con la ocurrencia del suceso. 
## 5.4
### Procedimientos y prácticas que funcionan bien 
Contribuyeron a reducir las consecuencias del suceso y a evitar un desenlace más grave el hecho de que 
a) el maquinista del tren de pasajeros detectó a tiempo que el tren de mercancías había entrado en su ruta de la vía y, por lo tanto, detuvo su tren sin demora (3.2.2), 
b) el agente de circulación encargado ejerció correctamente la comunicación crítica para la seguridad con el fin de detener el tren de pasajeros. 
## 5.5
### Lecciones aprendidas 
De haberse cumplido las normas de observación de las señales, el accidente habría podido evitarse. 


## Página 18


## Página 19

## ANEXOS 
Los datos de hechos que tuvieron una influencia esencial en el suceso y/o en su investigación y que no se han expuesto de otra forma en el informe final. 
Anexo 1 
### Los registradores de datos de los vehículos ferroviarios 
Figura 1: detalle del registro del tren de mercancías 
Figura 2: gráfico velocidad-tiempo generado a partir de los datos MFB del tren de pasajeros 


## Página 20

### Anexo 2 Lista de sucesos del registrador de datos DGP del Dispositivo de Enclavamiento 


## Página 21


## Página 22

Anexo 3 
### Normas citadas 
### La Instrucción de Señales número F.1 de MÁV 
## - 
### 1.2.24. Señal 
- 
Modo de transmisión con un contenido de información determinado, empleado en la explotación ferroviaria. La señal es una orden que indica al personal obligado a observar la señal la ejecución inmediata de alguna maniobra de servicio o medida de seguridad. 
## - 
### 3.1.1. Aplicación y funcionamiento del indicador de cabina de conducción 
- 
El indicador de cabina de conducción hace referencia al aspecto de la señal principal de la siguiente luz y, además de las preseñales, indica también que: 
- 
el tren ha pasado junto a una señal principal que da la señal «¡Alto!» y ha llegado a un tramo de vía ocupado o no equipado para la influencia en el tren, así como también que 
- 
el dispositivo no funciona porque se ha vuelto inutilizable, o el tren ha llegado a un tramo de vía no equipado para la influencia en el tren. 
### 3.2. Señales del indicador de cabina de conducción 
## - 
En los locomotores y coches de mando equipados con indicador de cabina de conducción digital, las señales aparecen con letras o números de color rojo. En los locomotores y coches de mando equipados con ETCS, las señales aparecen con letras o números de color negro en la pantalla gráfica táctil. 
En los locomotores y coches de mando no equipados con indicador de cabina de conducción digital, las señales aparecen de acuerdo con las figuras números 119 y 125. 
## - 
### 3.2.6. No llega una señal evaluable desde la vía. 
- 
Una luz blanca (figura 125). En el indicador de cabina de conducción digital, tres líneas horizontales (figura 126). En el indicador de cabina de conducción ETCS, tres líneas horizontales negras sobre fondo blanco (figura 127). 
- 
El dispositivo es inutilizable, o el tren ha llegado desde un tramo de vía no equipado para la influencia en el tren a un tramo equipado para la influencia en el tren pero ocupado, o bien el tren ha llegado a un tramo de vía que no está equipado para la influencia en el tren.  
- 
### 3.2.4. En la siguiente señal hay señal de ¡Alto! Prepararse para detenerse. 
- 
Una luz amarilla (figura 119). En el indicador de cabina de conducción digital, el número 0 (cero) (figura 120). En el indicador de cabina de conducción ETCS, la indicación del número 0 (cero) en negro sobre fondo amarillo (figura 121). 


## Página 23

## - 
### La Instrucción de Circulación número F.2 de MÁV 
## - 
### Obligación de vigilancia 
- 
16.2.2. En marcha, el maquinista situado en la cabeza del tren y el segundo trabajador que se encuentra junto al maquinista, y en el caso de un tren empujado, el acompañante que se encuentra en el primer vehículo, están obligados a vigilar mirando hacia delante y hacia atrás 
— las señales de advertencia, las señales dadas por las señales y los aparatos de señalización, 
- 
El maquinista está obligado a regular la velocidad del tren de modo que pueda observar las señales y pueda detener el tren antes de la señal que prohíbe la continuación de la marcha. 
## - 
### Procedimiento al sobrepasar la señal de ¡Alto! 
- 
### 16.2.4. Si el maquinista solo pudo detener el tren después de la señal principal que da la señal de ¡Alto! o de la señal de ¡Alto! establecida y preseñalada, así como del Límite de seguridad a considerar, entonces, después de la detención, está obligado a examinar, conjuntamente con el encargado de maniobras de la línea, el revisor jefe o el trabajador que presta servicio vigilando a su lado —y, en el caso de un tren que circula sin acompañante, por sí solo— el funcionamiento de los frenos tenidos en cuenta desde el punto de vista de la detención del tren, así como a determinar la causa del sobrepaso de la señal. El suceso debe calificarse como accidente incluso si del sobrepaso de la señal de ¡Alto! no se derivó ningún accidente. 
### Instrucción de Freno E.2 
### 7.1. Actuaciones en caso de avería del dispositivo de freno del locomotor 
El dispositivo de freno en servicio del locomotor no debe ser eliminado ni siquiera parcialmente. Está prohibido acuñar el dispositivo de desfogue.  


## Página 24

Anexo 4 
### Pruebas 
El VB realizó una prueba con el locomotor entre Győr - Rendező y Győr para comprobar el funcionamiento del dispositivo EVM. 
Durante la prueba, de acuerdo con las señales recibidas en las señales, llegó la corriente de señal adecuada del circuito de raíl de 75 Hz y del cable radiante. El dispositivo EVM evaluó los cambios de señal de acuerdo con los tiempos de retardo y, a continuación, el DVJ mostró los aspectos de señal. La función de frenado de emergencia del dispositivo también fue probada; funcionó correctamente y detuvo el locomotor. 
Durante la prueba, el Vb no observó anomalías en el funcionamiento del dispositivo EVM.
