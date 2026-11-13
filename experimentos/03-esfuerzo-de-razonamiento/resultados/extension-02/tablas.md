## Extensión 02: matriz por modelo

La extensión registró **122 observaciones principales**: 121 evaluables, con 110 resueltas y 11 fallos funcionales; 1 bloqueo del adaptador queda fuera del denominador funcional. Los 3 pilotos y 16 sondeos están excluidos. Hubo 0 interrupciones por cuota y 0 timeouts principales.

La referencia de gpt-6.1-sol usa 72 corridas originales y 48 de xhigh/max; excluye los ocho controles high de la extensión 01. No se fusionan sus tandas con la extensión 02. Los CSV anteriores siguen intactos.

«Evaluables» excluye cuota e infraestructura. Las medianas incluyen resueltas y fallos funcionales con datos disponibles; los denominadores de segundos y tokens se indican entre paréntesis. Una celda sin muestra no significa cero aciertos. «Pendientes» cuenta las corridas principales que nunca se iniciaron, no el bloqueo ya observado.

| Modelo | Nivel | Observadas / previstas | Resueltas / evaluables | Segundos mediana (n) | Tokens mediana (n) | Fuera de alcance / evaluables | Pendientes |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-6.1-sol | low | 24/24 | 24/24 | 41,088 (24) | 95.548,5 (24) | 0/24 | 0 |
| gpt-6.1-sol | medium | 24/24 | 24/24 | 46,499 (24) | 99.625,0 (24) | 0/24 | 0 |
| gpt-6.1-sol | high | 24/24 | 24/24 | 63,892 (24) | 118.101,0 (24) | 0/24 | 0 |
| gpt-6.1-sol | xhigh | 24/24 | 24/24 | 96,503 (24) | 130.560,0 (24) | 0/24 | 0 |
| gpt-6.1-sol | max | 24/24 | 24/24 | 102,009 (24) | 132.109,5 (24) | 0/24 | 0 |
| gpt-6-luna | low | 24/24 | 13/24 | 38,928 (24) | 124.518,5 (24) | 0/24 | 0 |
| gpt-6-luna | medium | 24/24 | 24/24 | 53,649 (24) | 128.182,0 (24) | 0/24 | 0 |
| gpt-6-luna | high | 24/24 | 24/24 | 63,050 (24) | 144.542,5 (24) | 0/24 | 0 |
| gpt-6-luna | xhigh | 24/24 | 24/24 | 107,519 (24) | 155.972,5 (24) | 0/24 | 0 |
| gpt-6-luna | max | 24/24 | 24/24 | 96,824 (24) | 148.684,0 (24) | 0/24 | 0 |
| claude-haiku-5-5 | low | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-haiku-5-5 | medium | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-haiku-5-5 | high | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-haiku-5-5 | xhigh | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-haiku-5-5 | max | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-opus-5-5 | low | 1/24 | 1/1 | 21,824 (1) | 31.334,0 (1) | 0/1 | 23 |
| claude-opus-5-5 | medium | 1/24 | Sin muestra evaluable | — (0) | — (0) | — | 23 |
| claude-opus-5-5 | high | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-opus-5-5 | xhigh | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| claude-opus-5-5 | max | 0/24 | Sin muestra evaluable | — (0) | — (0) | — | 24 |
| fable | — | 0 / sin definir | Sin muestra atribuible | — (0) | — (0) | — | Sin definir: identidad |

### Cobertura y cierres de los bloques nuevos

| Modelo solicitado | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |
|---|---|---:|---:|---:|---:|---:|---|
| gpt-6-luna | completo | 120 | 120 | 0 | 1 | 5 | Retoma sólo nunca iniciadas tras ENMIENDA-02-01 |
| claude-haiku-5-5 | incompleto | 0 | 0 | 120 | 1 | 5 | permisos_incompatibles |
| claude-opus-5-5 | incompleto | 2 | 1 | 118 | 1 | 5 | permisos_incompatibles |
| fable | no_disponible | 0 | 0 | Sin definir | 0 | 1 | identificador_no_verificable |

### Razón nivel más alto / nivel más bajo

Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.

| Modelo | Niveles | Segundos nivel bajo | Segundos nivel alto | Razón tiempo | Tokens nivel bajo | Tokens nivel alto | Razón tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-6.1-sol | max/low | 41,088 | 102,009 | 2,483 | 95.548,5 | 132.109,5 | 1,383 |
| gpt-6-luna | max/low | 38,928 | 96,824 | 2,487 | 124.518,5 | 148.684,0 | 1,194 |
| claude-haiku-5-5 | max/low | — | — | No comparable: cobertura incompleta | — | — | No comparable |
| claude-opus-5-5 | max/low | — | — | No comparable: cobertura incompleta | — | — | No comparable |
| fable | — | — | — | No comparable | — | — | No comparable |

### Luna por tarea: resueltas sobre tres repeticiones

| Tarea | low | medium | high | xhigh | max |
|---|---:|---:|---:|---:|---:|
| 01-lotes | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 02-intervalos | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 03-importes | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 04-espera | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 05-consulta | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 06-inventario | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 07-planificador | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| 08-cache | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |

### Todos los fallos funcionales de Luna

| ID | Tests aprobados / total | Segundos | Tokens totales |
|---|---:|---:|---:|
| principal-02-intervalos-low-3 | 2/3 | 35.934 | 127853 |
| principal-04-espera-low-2 | 0/2 | 16.975 | 52269 |
| principal-04-espera-low-1 | 0/2 | 18.601 | 65486 |
| principal-05-consulta-low-1 | 0/3 | 23.05 | 93848 |
| principal-03-importes-low-3 | 0/2 | 17.595 | 52066 |
| principal-04-espera-low-3 | 0/2 | 53.194 | 123877 |
| principal-01-lotes-low-1 | 0/3 | 16.32 | 57099 |
| principal-08-cache-low-1 | 0/1 | 33.158 | 105264 |
| principal-08-cache-low-2 | 0/1 | 34.541 | 89032 |
| principal-01-lotes-low-3 | 0/3 | 22.258 | 65732 |
| principal-03-importes-low-2 | 0/2 | 26.905 | 80168 |

### Sólo corridas resueltas

| Modelo | Nivel | n | Segundos mediana (n) | Tokens mediana (n) | Líneas tocadas mediana |
|---|---|---:|---:|---:|---:|
| gpt-6.1-sol | low | 24 | 41,088 (24) | 95.548,5 (24) | 34,5 |
| gpt-6.1-sol | medium | 24 | 46,499 (24) | 99.625,0 (24) | 32,5 |
| gpt-6.1-sol | high | 24 | 63,892 (24) | 118.101,0 (24) | 34,0 |
| gpt-6.1-sol | xhigh | 24 | 96,503 (24) | 130.560,0 (24) | 35,0 |
| gpt-6.1-sol | max | 24 | 102,009 (24) | 132.109,5 (24) | 33,5 |
| gpt-6-luna | low | 13 | 43,224 (13) | 157.199,0 (13) | 94,0 |
| gpt-6-luna | medium | 24 | 53,649 (24) | 128.182,0 (24) | 38,5 |
| gpt-6-luna | high | 24 | 63,050 (24) | 144.542,5 (24) | 38,0 |
| gpt-6-luna | xhigh | 24 | 107,519 (24) | 155.972,5 (24) | 43,5 |
| gpt-6-luna | max | 24 | 96,824 (24) | 148.684,0 (24) | 42,0 |
| claude-haiku-5-5 | low | 0 | — (0) | — (0) | — |
| claude-haiku-5-5 | medium | 0 | — (0) | — (0) | — |
| claude-haiku-5-5 | high | 0 | — (0) | — (0) | — |
| claude-haiku-5-5 | xhigh | 0 | — (0) | — (0) | — |
| claude-haiku-5-5 | max | 0 | — (0) | — (0) | — |
| claude-opus-5-5 | low | 1 | 21,824 (1) | 31.334,0 (1) | 44,0 |
| claude-opus-5-5 | medium | 0 | — (0) | — (0) | — |
| claude-opus-5-5 | high | 0 | — (0) | — (0) | — |
| claude-opus-5-5 | xhigh | 0 | — (0) | — (0) | — |
| claude-opus-5-5 | max | 0 | — (0) | — (0) | — |

### Uso e interpretación de los recibos

Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.

Los comandos exactos, versiones, montajes y límites están en [OPERACION-02.md](../OPERACION-02.md) y [aislamiento.json](extension-02/aislamiento.json). La reconexión recuperada de una observación de Luna se documenta en [ENMIENDA-02-01.md](../ENMIENDA-02-01.md), con original, hashes y reclasificación auditables; no se repitió la observación ni se alteraron sus tiempos, tokens o tests.
