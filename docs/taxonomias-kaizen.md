# Taxonomías KAIZEN — conceptos de filtrado (Fase 2)

Fuente: `Estructura Informe Investigación FINAL.docx` (KAIZEN, 16-07-2026) — estructura mínima del informe de investigación según RD 929/2020, RD 623/2014 y Reglamento (UE) 2020/572.

Estas categorías se extraerán con IA (Fase 2) de cada informe y se añadirán como campos
adicionales del JSON de cada suceso, para permitir consultas tipo:
"accidentes en plena vía, red convencional, con ASFA, explotación degradada y factor humano".

## Red y explotación (sección 2.2.5)

| Campo | Valores |
|---|---|
| `caracterizacion_red` | estación · terminal_mercancias · plena_via |
| `tipo_red` | alta_velocidad · convencional · cercanias · media_distancia · ancho_metrico · otros |
| `trafico_linea` | viajeros · mercancias · mercancias_peligrosas · mixto |
| `explotacion` | nominal · degradada |
| `proteccion_tren` | ASFA · ERTMS · LZB · otro · ninguno |
| `material_implicado` | viajeros · mercancias · mantenimiento · obras |
| `tramo_obras` | sí/no |
| `punto_riesgo` | sí/no (listado de puntos de riesgo) |
| `ltv` | valor de la limitación temporal de velocidad |
| `elementos_red` | aparato_de_via · tunel · viaducto · paso_a_nivel · cruce_andenes · zona_derrumbes · zona_inundable · tramo_cerrado |

## Subsistema afectado (2.2.4)

infraestructura · energia · cms_en_via · cms_a_bordo · material_rodante_adif · material_rodante_operador · explotacion_gestion_trafico · mantenimiento · aplicaciones_telematicas

## Circunstancias externas (2.4.1)

| Campo | Valores |
|---|---|
| `viento` | sí/no + umbral_superior sí/no |
| `precipitacion` | sí/no + umbral_superior sí/no |
| `sismo` | sí/no |
| `hielo` | sí/no |
| `zona_inundable` | sí/no |
| `luz` | natural · artificial |
| `temperatura_extrema` | umbral_superior · umbral_inferior · no |
| `visibilidad` | descripción libre |

## Factor humano (3.6)

| Campo | Valores |
|---|---|
| `factor_humano` | sí/no |
| `factor_humano_origen` | adif · adif_av · otro_gestor · empresa_ferroviaria · contratistas |
| `tiempo_trabajo` | relevante/no |
| `circunstancias_medicas` | sí/no |
| `tension_fisica_psicologica` | sí/no |
| `diseno_ihm` | sí/no |

## Víctimas y daños (2.3)

- víctimas por categoría: viajeros · personal_ferroviario · terceras_personas
- daños: carga · material_rodante · infraestructura · medio_ambiente · impacto_economico

## Recomendaciones (4.6)

- tipo: tecnica_aesf · observacion_asbo · observacion_isa
- destinatario: adif · adif_av · otro_gestor · empresa_ferroviaria · ingenieria · contratistas · otros
- fase_ciclo_vida: concepto · diseño · fabricación · pruebas_validación · explotación_mantenimiento · retirada_servicio

## Cadena de causas (4.3) — mapea al schema actual

- `causa_directa` ← 4.3.1 causas directas e inmediatas
- `factores_coadyuvantes` ← 4.3.2 (NUEVO en schema v2)
- `causas_subyacentes` ← 4.3.3/4.3.4/4.3.5 (cualificaciones+mantenimiento, marco normativo, SGS)
