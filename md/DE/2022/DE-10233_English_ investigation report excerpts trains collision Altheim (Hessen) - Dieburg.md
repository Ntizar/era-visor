---
pais: DE
anio: 2022
idioma: EN
pdf: DE-10233_English_ investigation report excerpts trains collision Altheim (Hessen) - Dieburg.pdf
url_oficial: https://www.era.europa.eu/system/files/2024-01/DE-10233_English_%20investigation%20report%20excerpts%20trains%20collision%20Altheim%20%28Hessen%29%20-%20Dieburg.pdf
md5_pdf: d1082371674ae482258e86260ac4e5e6
paginas: 14
chars: 32825
tablas: 1
cuerpo: "11.0pt; encabezados 0 niveles"
rotulos_excluidos: "13 (page # of #)"
verbatim_fallos: 0
escaneado: false
paginas_sin_texto: 0
fecha_proceso: 2026-11-18
generador: convertir_md_pais.py (PyMuPDF 2.1, dict tipográfico)
---
## Página 1

Translation of an excerpt of the investigation report  
“Train collision Altheim (Hesse) halt – Dieburg station on 19/05/2022”  
Status as of 11/12/2023, version 1.0. 
Note: 
In accordance with Article 3 of Implementing Regulation (EU) 2020/572, points 1, 5 and 6 of Annex I of 
an investigation report shall be written in a second official European language. This translation should 
be available no later than three months after the delivery of the report.  
The following English translation is a corresponding excerpt of the investigation report. The German 
language version is authoritative. 
Excerpt translation: 
1 Summary 
The first section contains a brief description of the event, as well as information on the consequences, 
primary causes and safety recommendations provided in the individual case. 
1.1 Brief description of the event 
On 19/05/2022 at 02:52 am, the train number (TN) of the DGS 46192, which was between 
Babenhausen and Dieburg, was automatically overwritten with the TN of the subsequent DGS 42174 
following a route cancellation. As a result, the DGS 46192 travelled onward towards Darmstadt, initially 
without a TN and then subsequently with the wrong TN of the DGS 42174. The DGS 42174 undetected 
remained on the route and came to a stop between the Altheim (Hesse) halt and Dieburg station. The 
Dieburg dispatcher ultimately reset the block section, which was still occupied by DGS 42174 without 
this having been detected. As a result, the subsequent GAG 60101 travelled on the block section at the 
signal position and collided with the stationary DGS 42174 at around 04:04 am. 
Page 1 of 14

## Página 2

### 1.2 Consequences 
As a result of the collision, the train driver of the GAG 60101 was fatally injured, and the train driver of 
the DGS 42174 suffered minor injuries. The traction unit (TU) and the first carriages of the colliding 
GAG 60101 and the last carriage of the DGS 42174 were significantly damaged. There was also a high 
level of material damage to the freight on the two trains and to the infrastructure. 
### 1.3 Causes 
The collision was due to a chain of events that originated in Babenhausen.  
Time
Contributing 
Systemic 
Factor  
Causal factor  
factor 
factor 
Issue 
02:52 am
Untimely advancing of the train 
F1  
X  
X  
number and overwriting of TN 
46192 with TN 42174 
02:53 am
Automatic deletion of TN 42174 
from block field 36 after manual 
F2 
X 
X 
new entry of the TN in the station 
field 
02:53 am
Original TN 46192 no longer 
F3 
X 
entered in block field 36 
02:56 am
Blank number in TN field 34 
F4 
X 
X 
deleted by Babenhausen 
dispatcher 
03:11 am
Dieburg dispatcher assumes there 
F5 
X 
X  
is a fault 
03:26 am
Driving on sight procedure 
F6 
X 
X 
incorrectly implemented (including 
entry signal 30F set) 
03:31 am
Timeout message in block section 
F7 
X  
X 
34 not observed 
03:32/03:35 am
F8 
X 
X 
Location query DGS 42174 
03:34 am
F9 
X 
Operation of axle counter reset  
03:06/03:39 am
No query from driver 46192 about 
F10 
X 
reason for signal stop 
Table 1: Summary of influencing factors 

## Página 3

### 1.4 Safety recommendations 
The following safety recommendations are issued in accordance with section 6 of the Eisenbahn­
Unfalluntersuchungsverordnung (EUV, German railway accident investigation regulation) and Article 
26(2) of Directive (EU) 2016/798. It is recommended that 
x
the working system for processing and transmitting train messages is examined and 
modified so that its information always complies with the requirements as per Reg. (EU) 
2018/762, Annex 2, point 4.4.3, in particular when transitioning between automated and 
manual processes. 
x
the processes for planning, running and approving the functions of TN systems should be 
examined and improved as per Reg. (EU) 2018/762 Annex II point 5.2.1, including the 
associated change and risk management, in order to ensure that the physical asset is 
integrated safely into the working systems. 
x
in order to ensure the protective function of the work procedure “the same train has 
entered a section and left it again” as per Reg. (EU) 2018/762 Annex II point 3.1.1.1, the 
risks in the event of errors by the people involved must be determined and the work 
procedure must be improved. 
x
according to Reg. (EU) 2018/762 Annex II point 3.1.1.1, the risks in the event of 
discrepancies between the location of a train assumed by the dispatcher and the location 
reported by the train driver must be determined and suitable work procedures must be 
developed for safe continuation of operation. 
x
the technical conditions for the effectiveness of the operator control action of an axle 
counter reset should be further developed in order to further minimise or exclude the risks 
of successful, untimely operator control actions. Until these measures are implemented 
technically, and in order to minimise potential damage, it is recommended that 
compensatory procedure­based solutions are implemented. 
## 5 
### Conclusions 
The following section contains a summary of the identified causal, contributing and systemic factors. 
In addition, two further subsections are provided containing information about measures already 
taken, and additional comments. 
## 5.1 
### Summary and conclusion  
The collision was due to a chain of events that originated in Babenhausen. The starting point was the 
automatic advancing and overwriting of a TN without train travel due to the planning of TN reporting 

## Página 4

system 800 in Babenhausen. Several causal, contributing and systemic factors resulted in the chain of 
events being continued by the people involved, which ultimately resulted in the collision. 
## 5.1.1 
### Classification of influencing factors 
The table below contains the summary of the influencing factors relevant for the chain of events. These 
are assigned to causal, contributing and systemic factors according to Regulation (EU) 2020/572 Article 
2. The numbers in brackets for the factors are used to aid assignment to the explanations in the 
chapters below. 
Partial aspect, 
Time 
Partial aspect, 
Partial aspect, systemic 
contributing 
causal factor  
factor 
Issue 
factor 
Untimely advancing 
02:52 am 
Newly implemented 
of the TN without a 
functionality does not 
(F1) Untimely advancing of 
train having moved, 
correspond to the 
the train number and 
with 
original performance of 
overwriting of TN 46192 with 
overwriting/deletion 
the TN system  
TN 42174 
of a normal TN  
Information 
02:53 am 
deleted without 
the knowledge 
Technical planning of 
(F2) Automatic deletion of TN 
and, if necessary, 
the printer output for 
42174 from block field 36 
cooperation of 
the deletion is absent 
after manual new entry of 
the dispatchers 
the TN in the station field 
involved 
Failure of 
02:53 am 
Babenhausen 
dispatcher, meaning 
(F3) Original TN 46192 no 
that a train was 
longer entered in block field 
moving on the route 
36 
without a TN 
02:56 am
Planning TN system 
Rules in guideline 
Babenhausen: technical 
(F4) Blank number in the TN 
408.0591 not 
access to TN field 34 
field 34 deleted by 
observed 
was possible 
Babenhausen dispatcher 

## Página 5

Incomplete work 
specifications in 
No clarification 
guideline 408.0591 in 
03:11 am 
about train journeys 
relation to missing 
(F5) Dieburg dispatcher 
that have been 
information in the TN 
assumes there is a fault 
made 
system with a 
simultaneous occupied 
display  
03:26 am
Error in application of 
Rule in guideline 
(F6) Driving on sight 
rules results directly in 
408.0248 not 
procedure incorrectly 
the failure of their 
observed 
implemented (including entry 
protective objectives 
signal 30F set) 
Ignoring of technically 
03:31 am 
Rule in guideline 
generated warnings 
408.0641 not 
(F7) Timeout message in 
due to planning errors 
observed  
block section 34 not observed
in the infrastructure 
Location details 
from driver 42174 
Procedure for 
03:32/03:35 am 
not taken into 
discrepancies in 
(F8) Location query DGS 
consideration by 
location information 
42174 
Dieburg 
not regulated 
dispatcher 
03:34 am
Last action that 
(F9) Operation of axle 
made the collision 
counting reset for block 
possible 
section 34 
03:06/03:39 am
Rules in guideline 
(F10) No query from driver 
408.2455 not 
46192 about reason for signal 
observed 
stop 
Table 6: Summary of influencing factors 

## Página 6

The diagram below provides another visual representation of the key steps in the chain of events in 
time order, separated according to the infrastructure manager (right) and railway undertaking (left). 
The causal factors mentioned above are indicated by red dots, while orange dots are used for the 
contributing factors. 
Figure 25: Timing of the chain of events 

## Página 7

### 5.1.2 TN systems 
As part of the adjustment measures for TN reporting system 800 in Babenhausen, individual technical 
and operational peculiarities emerged on the Dieburg computer­based interlocking, which caused the 
start and contributed to the further progression of the chain of events. 
### Causal factor 
For F1: When cancelling an only preset outward train route, the Babenhausen TN system removed an 
automated train message without there having been an actual train movement with signal proceed 
aspect and halt aspect. At the same time, with this untimely deregistration, the TN system overwrote 
a TN saved in block section 36 of a train that had previously left properly and been deregistered 
automatically. Contrary to Regulation (EU) 2018/762 Annex II point 4.4.3 c), the safety­related 
information generated/altered in these situations was not correct. It did not match the actual 
operations. An automated deregistration must only take place as the result of a train journey that has 
actually happened. The TN system must therefore behave according to the permitted processes for 
telephonic train reporting procedures, according to which telephonic deregistration only takes place if 
there has been an actual train journey. A saved TN for an actual train journey should not be able to be 
overwritten due to automated, untimely deregistration. Data loss of this kind must be avoided. 
### Contributing factor 
For F2: The automated deletion of the TN that was in block section 36, triggered by the manual new 
entry, resulted in a change to the data for operations on the route without other people involved 
knowing or being aware of this. Before a manual or automated deletion of a TN on the route, all people 
involved should be informed accordingly or agree based on a defined work procedure, analogously to 
the processes for telephonic train message procedures. 
### Systemic factors 
For F1: The data processing in the TN system, which was newly set up during the adjustment and as a 
result was not correct or consistent, seems to have been neither identified in the infrastructure 
manager’s planning and implementation process nor assessed in terms of acceptability and sufficient 
control via appropriate work instructions. The infrastructure manager’s processes for planning, 
implementation and introduction of altered behaviour of TN systems as physical assets must identify 
and assess risks in accordance with Regulation (EU) 2018/762 Annex II point 5.2.1 in conjunction with 
point 3.1.2. If, as a result of this, additional measures are required, they must also be incorporated into 
the risk management and corresponding work instructions must be introduced for the operators.  
For F2: After the TN had been entered manually again in a TN field of Babenhausen station following 
the explained incorrect deregistration, the TN system did not simultaneously log the automated 
deletion of the deregistration saved in block section 36. Although the monitor output of the TN system 
showed the situation that the dispatcher wanted, the printer log did not reflect this situation. Contrary 
to Regulation (EU) 2018/762 Annex II point 4.4.3 d), the safety­related information was therefore no 
longer consistent. In contrast, handwritten logs of telephonic train messages remain unchanged in a 
scenario such as this, or agreed changes are cancelled by the people involved in accordance with 
specifications. The deletion of a TN that has been deregistered must remain traceable. 

## Página 8

For F4: According to the planning of the TN system, the Babenhausen dispatcher had access to TN field 
34, which contains important data within the knowledge and decision­making authority of the Dieburg 
dispatcher about trains travelling towards him. Contrary to Regulation (EU) 2018/762 Annex II point 
4.4.3 f), this meant that it was possible for safety­related information to be deleted without the 
responsible Dieburg dispatcher being aware of this. In order to prevent “manipulation” of data for 
which another person involved is responsible, the access authorisation of the Babenhausen dispatcher 
must be withdrawn.  
## 5.1.3 
### Babenhausen dispatcher 
During the cancellation of the outward train route for the DGS 42174, the Babenhausen dispatcher 
noticed the technically required advancement of TN 42174 into the still­occupied block section 36 and 
manually re­entered TN 42174 in his station track 301. According to the functionality of the TN 
reporting system 800, TN 42174 in TN field 36 was automatically deleted again. 
### Causal factor 
For F3: The Babenhausen dispatcher failed to re­enter the previously overwritten TN of DGS 46192 
into TN field 36. Although sufficient information was available, he did not notice that DGS 46192, which 
had previously been released, was still in block section 36. On the operating console in Babenhausen 
signal box, block section 36 had an occupied display (illuminated red). It could be seen from the TN 
monitor that DGS 46192 had not yet moved into the next block section 34, therefore it still had to be 
in section 36. In addition, the TN printer documented the overwriting with the note “46192 overwritten 
with 42174”. Obviously, at this time, the Babenhausen dispatcher was no longer aware of the DGS 
46192 and he therefore failed to re­enter TN 46192, which had unintentionally been overwritten 
automatically, in TN field 36. Consequently, a train without a TN was travelling on the route. 
### Contributing factor 
For F4: Due to the failure mentioned above, it was possible for the DGS 46192 to change from block 
section 36 to block section 34 without being noticed by the two dispatchers, and it generated a blank 
number there. The Babenhausen dispatcher noticed the blank number and possibly attributed this to 
the unintentional automatic TN advancing that had previously taken place. Although block section 34 
was no longer part of his area of responsibility, he had access to this TN field and was able to delete 
the blank number. The associated signal­related occupied report for block section 34 was not displayed 
to him because it was outside of his adjusting range. Irrespective of the fact that he was not 
responsible, according to guideline 408.0591 section 3, agreement with the responsible Dieburg 
dispatcher and querying of the location of the train journeys would have been mandatory before the 
deletion. Operational reliability in the event of faults must be improved and awareness must be raised 
of the need for and the application of rules. 
5.1.4 
Dieburg dispatcher 
As was shown by the train radio conversations, at the time of the “disappearance” of the TN of the 
DGS 46192 caused by Babenhausen, the Dieburg dispatcher was dealing with operations at another 

## Página 9

point in his adjusting area. It is possible that he did not directly observe the prohibited deletion of the 
blank number by the Babenhausen dispatcher, or the previous overwriting of the TN of the DGS 46192. 
This was not unlikely due to the size of the workstation and the tasks for a computer­based interlocking 
dispatcher.  
### Causal factors 
For F5: From the perspective of the Dieburg dispatcher, there was no reason to question the 
(incomplete) information in the TN system and to look for a missing train. He interpreted the occupied 
display in block section 34 without a saved TN as an axle counting fault.  
For F6: Accordingly, the Dieburg dispatcher handled the supposed fault in block section 34 according 
to the rules in guideline 408.0248 “most recently moved train undetectable”. However, the dispatcher 
did not implement the specifications from the guidelines. He failed to have the DGS 42174, which had 
been given an instruction, stop at entry signal 30F and to determine the location and TN again. Instead, 
he prematurely set entry signal 30F to travel, as a result of which the protective target of the 
specifications from the guidelines was significantly undermined. The rule is intended to ensure that 
only one and the same train can go through this section in full and that there is no confusion with 
another train that is driving ahead undetected. However, the open position meant that the DGS 46192, 
which was waiting undetected at the entry signal, entered and travelled through the station instead of 
the expected DGS 42174, and the Dieburg dispatcher then carried out a clearance check for DGS 42174 
with a mistaken assessment of the end of the train of the DGS 46192. According to Regulation (EU) 
2018/762 Annex II point 4.3, within an organisation it must be ensured that employees entrusted with 
tasks that affect safety are aware of the relevance, importance and the consequences of their 
activities. In accordance with point 6.1.2 of the aforementioned Regulation, the performance of safety­
related tasks must be monitored and there must be intervention if these tasks are not being performed 
properly. The infrastructure manager’s evidence of training and further education/monitoring did not 
clearly show whether the Dieburg dispatcher was appropriately aware of the protective objectives of 
the regulation. 
For F9: Although the observation of the end of the train by the Dieburg dispatcher was carried out 
according to the rules, due to the aforementioned error this was for the wrong train. The operation of 
the axle counting reset based on this resulted in an operating status that was actually safe (occupied 
display) turning into a potentially unsafe status (block section free), which simultaneously had a very 
high potential level of damage. The aim must be to reduce the possible level of damage if there is a 
certain risk of established work procedures being carried out incorrectly.  
An appropriate, temporary procedure­based approach to reduce the possible level of damage is to 
implement the principle, which has been considered increasingly in recent years, that “in the event of 
a fault the first train drives on sight” even if travel has indeed been approved with the main signal, but 
auxiliary actions in the signal box would be required in advance for this purpose. This does not reduce 
the probability of the prohibited situation of two trains being in the same section, but driving on sight 
would considerably reduce the level of potential damage. 
A technical approach would be to use technical further developments already available in the railway 
sector for the axle counting reset, such as the “preparatory axle counting reset” already used by other 
infrastructure managers. Further possible technical solutions have already been developed by the 
industry and are being advanced using studies. For example, a research project by the German Centre 

## Página 10

for Rail Traffic Research [Deutsches Zentrum für Schienenverkehrsforschung, DZSF] at the Federal 
Railway Authority [Eisenbahn­Bundesamt)] entitled “Supporting measures when carrying out auxiliary 
operating actions1” promises interesting approaches. 
### Contributing factors 
For F8: When identifying the end of the train, the Dieburg dispatcher did indeed notice that the travel 
time and speed of the observed train were not consistent and under no circumstances could they have 
been the result of driving on sight according to the rules. In order to resolve this discrepancy, he 
correctly attempted to contact the driver of the DGS 42174. He was repeatedly given correct and clear 
location details by the driver. Although, according to the valid procedural regulations, these location 
reports provide a fall­back level for elements that are faulty or not working properly, the Dieburg 
dispatcher did not give the necessary credence to the location details from driver 42174. He continued 
to trust the displays of his reporting equipment (TN system), which was not secure in terms of the 
technical signals. Evidently, the Dieburg dispatcher did not succeed in reflecting the situation and 
correcting it himself if necessary. He even continuously attempted to persuade driver 42174 of a 
different location, which according to analysis of the recorded train radio conversations he repeatedly, 
and towards the end even emphatically, answered with incomprehension.  
For F7: A timeout message generated by DGS 46192 at 03:31 am in block section 34 was not processed 
by the Dieburg dispatcher according to the regulations, possibly out of habit. The timeout message in 
the section illuminated red at this time (during or after the observation of the end of the train) was a 
clear indication of actual train travel and not the result of a fault. Even though the operational 
measures in the event of a timeout message from remotely monitored crossings primarily aim to avoid 
crossing accidents, as a side effect dealing with the message in accordance with the rules may have 
resulted in reflection on own actions in the specific situation and may possibly have resulted in the 
Dieburg dispatcher noticing the DGS 46192. Operational reliability in the event of faults must be 
improved and awareness must be raised of the need for and the application of rules.  
### Systemic factors 
For F5: Judging from the train radio conversations, the Dieburg dispatcher assumed that there was an 
axle counting fault left by a train that had previously travelled in block section 34. The regulations in 
guideline 408.0591 section 3 contain no instructions on what to do if no TN is displayed in a TN field of 
a section that is displayed as occupied. They do not even refer to the work instructions for an identified 
occupied display (here guideline 408.0248) for a track section. The regulations in guideline 408.0591 
should be supplemented for the scenario “no TN in the TN field” with simultaneous occupied display.  
For F6: The operationally important procedure for protecting against confusing an incoming train with 
a train that is still advancing undetected in the same section depends on the correct actions of a single 
person. The process should be designed suitably so that the dispatcher is forced to wait for the 
involvement and result message from another person involved, e.g. the driver, to protect against his 
own incorrect actions.  
For F7: Evidently, the dispatchers in Dieburg generally did not have the necessary awareness of the 
need to apply the rules in the event of a timeout. The risks of unwanted operating statuses with 
1 DZSF - projects - German title: Unterstützungsmaßnahmen bei der Durchführung von betrieblichen 
Hilfshandlungen (bund.de) dated 09/08/2023 

## Página 11

resulting frequent technical warnings were obviously not highlighted sufficiently during the 
infrastructure planning, and the consequences of this were not considered. According to Regulation 
(EU) 2018/762 Annex II point 5.2.1, the organisation must manage safety risks associated with physical 
assets and fulfil the requirements related to human factors. Where trains may be stopped, the 
occurrence of timeout messages must already be considered when planning the infrastructure.  
For F8: In the event of contradictory location information from the driver on the one hand and 
technical systems, such as the TN system, on the other hand, there are two equal sources available to 
the dispatcher. As the decision­maker, he is free to judge and select which information he gives 
credence to. An additional decision maker using reliable information should therefore be incorporated 
in order to ensure clarification of the correct information. Until there is a decision from this decision 
maker, continuing operations does not seem advisable. 
## 5.1.5 
### Driver 46192 
The DGS 46192 was stationary for around 21 minutes at entry signal 30F of Dieburg station and also 
for around 25 minutes until the incident at Darmstadt­Kranichstein entry signal, without reporting to 
the dispatcher within five minutes in each case.  
### Contributing factor 
For F10: If driver 46192 had asked the Dieburg dispatcher about the reason for the stoppage during 
these periods as per the regulation specifications, his TN would have come to the attention of the 
Dieburg dispatcher again. It must be noted that this regulation is largely optional. During the period in 
consideration, it was also not fully implemented by other drivers of other trains not involved in the 
incident because before embarking on the route they had already been informed about expected 
operational difficulties. It was not possible to determine whether driver 46192 had also been given this 
information. 
## 5.1.6 
### Observations about TN systems 
The telephonic train messages procedure is used by the dispatcher for safety­related information 
about train journeys and for the scheduling of these journeys. The technical safety system is largely 
used to protect the succession of trains. The information about which train journey with which 
characteristics is coming up to a station or stop and how it must be handled there according to the 
schedule specifications must be seen as safety­related, even if there is an effective signalling block 
system. In the event of a fault at the latest, the telephonic train message procedure then also has the 
sole task of ensuring that the succession of trains move with the right spacing. The transition from 
normal to malfunction mode is therefore critical in relation to the mandatory correctness and 
consistency of the data that the people involved continue to use. Technical systems incorporated into 
a safety­related work system must therefore be created so that, on the transition to malfunction mode, 
they directly provide reliable information about operations. If necessary, supplementary work 
processes must be used to compare the correctness and consistency of the data available with the 
current operating status. In addition, the supporting technical systems should not be a source of error 
themselves. The awareness of the infrastructure manager is therefore very important for the 

## Página 12

relationships between appropriate planning, performance and monitoring of operations and inherent 
procedures. 
TN systems are not secure reporting systems from a technical signalling perspective, but, in the case 
of computer­based interlocking in particular, they are integrated into secure technical signalling 
displays and displayed on the operating monitors. The Dieburg dispatcher did not seem to be fully 
aware of the discrepancy between the two display types. He believed that the incorrect TN display and 
advancement of TN 42174 was more important than the clear and correct location information from 
driver 42174. It therefore seems to be necessary to raise awareness among operating personnel of the 
limited significance of TN systems, and also to critically scrutinise the organisation of the human­
machine interface.  
In spite of the unresolved contradiction between his technical notification displays and the location 
information from driver 42174, the Dieburg dispatcher produced a block reset for section 34. The 
information available from the non­secure display of his TN system was the basis for the dispatcher 
carrying out the axle counting reset, i.e. for an intervention in the secure signal technology that had 
serious consequences. Interventions in the secure signal technology must not be made solely on the 
basis of findings made based on displays on notification equipment that is not secure from a technical 
signalling perspective. 
## 5.1.7 
### Conclusion 
Operationally implausible functions of the TN reporting system 800 in Babenhausen in conjunction 
with operating errors by the Babenhausen dispatcher resulted in a train without a TN saved in the TN 
system travelling on the route between Babenhausen and Dieburg. The data saved in the TN system 
did not reflect the actual operations and encouraged the Dieburg dispatcher to make incorrect 
decisions based on this information. In spite of other indications of a train journey, the Dieburg 
dispatcher incorrectly assessed the technical occupied report for block section 34 as an axle counting 
fault. Further errors in the application of the rules in conjunction with solely relying on the correctness 
of the TN system display, which is not secure in terms of signal technology, resulted in a serious 
misinterpretation of the actual operational situation by the Dieburg dispatcher. As a result of this, he 
reset block section 34, which ultimately resulted in the trains colliding.  
The entire working system for processing and transmitting train messages is directly relevant for 
safety. It must be ensured that this system always provides sufficient safety, even when switching from 
normal mode to malfunction mode. This relates, in particular, to the routines for adding or correcting 
information that was previously processed, transmitted or archived automatically, and which then, in 
particular when faults occur or are assumed to have occurred, is a new factor to be incorporated into 
subsequent decisions on further actions by operating personnel. 
## 5.2 
### Measures taken since the event  
Following the event, DB Netz AG issued service order 2022­46 to the Babenhausen and Dieburg signal 
boxes. This governed the operational procedure for releasing a route in the direction of Dieburg.  
DB Netz AG is examining whether there can be further development of the software for the TN 
reporting system 800 in Babenhausen. Using an earlier software version is not possible. 

## Página 13

DB Netz AG has taken measures relating to the increasing occurrence of timeout messages. The 
dispatcher received training and targeted monitoring relating to this issue. At the same time, DB Netz 
AG is examining further measures to eliminate the cause of the frequent messages, e.g. altered signal 
locations for the block signals. 
## 5.3 
### Additional observations 
None 
## 6 
### Safety recommendations 
The following safety recommendations are made in accordance with section 6 of the EUV [German 
railway accident investigation regulation] and Article 26(2) of Directive (EU) 2016/798: 
No.
Addressee and safety recommendation
Relates to company
01/2023
Safety authority:
IM
It is recommended that the working system for 
processing and transmitting train messages is 
examined and modified so that its information always 
complies with the requirements as per Reg. (EU) 
2018/762, Annex 2, point 4.4.3, in particular when 
transitioning between automated and manual 
processes. 
02/2023
Safety authority:
IM
It is recommended that the processes for planning, 
running and approving the functions of TN systems 
should be examined and improved as per Reg. (EU) 
2018/762 Annex II point 5.2.1, including the associated 
change and risk management, in order to ensure that 
the physical asset is integrated safely into the working 
systems.  
03/2023
Safety authority:
IM
It is recommended that, in order to ensure the 
protective function of the work procedure “the same 
train has entered a section and left it again” as per Reg. 
(EU) 2018/762 Annex II point 3.1.1.1, the risks in the 
event of errors by the people involved must be 
determined and the work procedure must be 
improved. 

## Página 14

| 04/2023 | Safetyauthority: Itisrecommendedthat accordingtoReg (EU) , . 2018/762AnnexIIpoint3111 therisksintheevent . . . , ofdiscrepanciesbetweenthelocationofatrain assumedbythedispatcherandthelocationreported bythetraindrivermustbedeterminedandsuitable workproceduresmustbedevelopedforsafe continuationofoperation . | IM |
| 05/2023 | Safetyauthority: Itisrecommendedthatthetechnicalconditionsforthe effectivenessoftheoperatorcontrolactionofanaxle counterresetshouldbefurtherdevelopedinorderto furtherminimiseorexcludetherisksofsuccessful , untimelyoperatorcontrolactions Untilthese . measuresareimplementedtechnically andinorderto , minimisepotentialdamage itisrecommendedthat , compensatoryprocedure­basedsolutionsare implemented . | IM |
