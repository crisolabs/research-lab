## Extensión 02: matriz por modelo

La extensión registró **388 observaciones principales**: 387 evaluables, con 367 resueltas y 20 fallos funcionales; 0 errores de infraestructura quedan fuera del denominador funcional. Los 4 pilotos y 20 sondeos están excluidos. Hubo 1 interrupciones por cuota y 8 timeouts principales.

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
| claude-haiku-5-5 | low | 24/24 | 24/24 | 18,553 (24) | 47.353,0 (24) | 14/24 | 0 |
| claude-haiku-5-5 | medium | 24/24 | 23/24 | 23,324 (24) | 56.000,5 (24) | 12/24 | 0 |
| claude-haiku-5-5 | high | 24/24 | 24/24 | 32,636 (24) | 61.617,0 (24) | 4/24 | 0 |
| claude-haiku-5-5 | xhigh | 24/24 | 24/24 | 57,091 (24) | 87.451,5 (24) | 2/24 | 0 |
| claude-haiku-5-5 | max | 24/24 | 24/24 | 166,074 (24) | 195.129,5 (24) | 0/24 | 0 |
| claude-opus-5-5 | low | 24/24 | 24/24 | 20,838 (24) | 37.178,5 (24) | 0/24 | 0 |
| claude-opus-5-5 | medium | 24/24 | 24/24 | 26,472 (24) | 41.283,0 (24) | 5/24 | 0 |
| claude-opus-5-5 | high | 24/24 | 24/24 | 30,887 (24) | 42.501,0 (24) | 14/24 | 0 |
| claude-opus-5-5 | xhigh | 24/24 | 24/24 | 52,110 (24) | 53.390,5 (24) | 21/24 | 0 |
| claude-opus-5-5 | max | 24/24 | 21/24 | 376,156 (24) | 260.660,0 (21) | 0/24 | 0 |
| claude-fable-5-2 | low | 4/24 | 4/4 | 30,766 (4) | 35.199,5 (4) | 0/4 | 20 |
| claude-fable-5-2 | medium | 5/24 | 5/5 | 32,674 (5) | 34.764,0 (5) | 0/5 | 19 |
| claude-fable-5-2 | high | 6/24 | 6/6 | 39,556 (6) | 37.257,5 (6) | 0/6 | 18 |
| claude-fable-5-2 | xhigh | 6/24 | 5/5 | 173,479 (5) | 85.600,0 (5) | 0/5 | 18 |
| claude-fable-5-2 | max | 7/24 | 2/7 | 600,159 (7) | 86.655,5 (2) | 0/7 | 17 |

### Cobertura y cierres de los bloques nuevos

| Modelo solicitado | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |
|---|---|---:|---:|---:|---:|---:|---|
| gpt-6-luna | completo | 120 | 120 | 0 | 1 | 5 | Retoma sólo nunca iniciadas tras ENMIENDA-02-01 |
| claude-haiku-5-5 | completo | 120 | 120 | 0 | 1 | 5 |  |
| claude-opus-5-5 | completo | 120 | 120 | 0 | 1 | 5 |  |
| claude-fable-5-2 | incompleto | 28 | 27 | 92 | 1 | 5 | cuota |

### Razón nivel más alto / nivel más bajo

Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.

Los tiempos incluyen los timeouts funcionales. Si falta el recibo final, los tokens quedan ausentes. El cociente de sus medianas usa sólo los datos disponibles, con n explícitos: no representa el consumo de las corridas sin recibo.

| Modelo | Niveles | Segundos nivel bajo (n) | Segundos nivel alto (n) | Razón tiempo | Tokens nivel bajo (n) | Tokens nivel alto (n) | Razón tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-6.1-sol | max/low | 41,088 (24) | 102,009 (24) | 2,483 | 95.548,5 (24) | 132.109,5 (24) | 1,383 |
| gpt-6-luna | max/low | 38,928 (24) | 96,824 (24) | 2,487 | 124.518,5 (24) | 148.684,0 (24) | 1,194 |
| claude-haiku-5-5 | max/low | 18,553 (24) | 166,074 (24) | 8,951 | 47.353,0 (24) | 195.129,5 (24) | 4,121 |
| claude-opus-5-5 | max/low | 20,838 (24) | 376,156 (24) | 18,051 | 37.178,5 (24) | 260.660,0 (21) | 7,011 (datos parciales) |
| claude-fable-5-2 | max/low | — | — | No comparable: cobertura incompleta | — | — | No comparable |

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

### Tareas con fallos: resueltas / evaluables por nivel

| Modelo | Tarea | low | medium | high | xhigh | max |
|---|---|---:|---:|---:|---:|---:|
| gpt-6-luna | 01-lotes | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gpt-6-luna | 02-intervalos | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gpt-6-luna | 03-importes | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gpt-6-luna | 04-espera | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gpt-6-luna | 05-consulta | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gpt-6-luna | 08-cache | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| claude-haiku-5-5 | 07-planificador | 3/3 | 2/3 | 3/3 | 3/3 | 3/3 |
| claude-opus-5-5 | 02-intervalos | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 |
| claude-opus-5-5 | 07-planificador | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| claude-fable-5-2 | 02-intervalos | Sin muestra | Sin muestra | Sin muestra | Sin muestra | 0/1 |
| claude-fable-5-2 | 04-espera | Sin muestra | 1/1 | Sin muestra | 1/1 | 0/1 |
| claude-fable-5-2 | 05-consulta | 1/1 | Sin muestra | 1/1 | 2/2 | 0/2 |
| claude-fable-5-2 | 08-cache | 1/1 | 1/1 | Sin muestra | 1/1 | 0/1 |

### Todos los fallos funcionales de la matriz

| Modelo | ID | Tests aprobados / total | Segundos | Tokens totales | Motivo |
|---|---|---:|---:|---:|---|
| gpt-6-luna | principal-02-intervalos-low-3 | 2/3 | 35.934 | 127853 | tests_fallan |
| gpt-6-luna | principal-04-espera-low-2 | 0/2 | 16.975 | 52269 | tests_fallan |
| gpt-6-luna | principal-04-espera-low-1 | 0/2 | 18.601 | 65486 | tests_fallan |
| gpt-6-luna | principal-05-consulta-low-1 | 0/3 | 23.05 | 93848 | tests_fallan |
| gpt-6-luna | principal-03-importes-low-3 | 0/2 | 17.595 | 52066 | tests_fallan |
| gpt-6-luna | principal-04-espera-low-3 | 0/2 | 53.194 | 123877 | tests_fallan |
| gpt-6-luna | principal-01-lotes-low-1 | 0/3 | 16.32 | 57099 | tests_fallan |
| gpt-6-luna | principal-08-cache-low-1 | 0/1 | 33.158 | 105264 | tests_fallan |
| gpt-6-luna | principal-08-cache-low-2 | 0/1 | 34.541 | 89032 | tests_fallan |
| gpt-6-luna | principal-01-lotes-low-3 | 0/3 | 22.258 | 65732 | tests_fallan |
| gpt-6-luna | principal-03-importes-low-2 | 0/2 | 26.905 | 80168 | tests_fallan |
| claude-haiku-5-5 | principal-07-planificador-medium-3 | 4/5 | 33.904 | 70020 | tests_fallan |
| claude-opus-5-5 | principal-07-planificador-max-3 | 5/5 | 600.169 | — | timeout_agente |
| claude-opus-5-5 | principal-02-intervalos-max-2 | 3/3 | 600.302 | — | timeout_agente |
| claude-opus-5-5 | principal-07-planificador-max-1 | 5/5 | 600.223 | — | timeout_agente |
| claude-fable-5-2 | principal-08-cache-max-2 | 0/1 | 600.226 | — | timeout_agente |
| claude-fable-5-2 | principal-04-espera-max-3 | 2/2 | 600.159 | — | timeout_agente |
| claude-fable-5-2 | principal-05-consulta-max-3 | 0/3 | 600.151 | — | timeout_agente |
| claude-fable-5-2 | principal-05-consulta-max-2 | 3/3 | 600.195 | — | timeout_agente |
| claude-fable-5-2 | principal-02-intervalos-max-1 | 3/3 | 600.174 | — | timeout_agente |

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
| claude-haiku-5-5 | low | 24 | 18,553 (24) | 47.353,0 (24) | 41,0 |
| claude-haiku-5-5 | medium | 23 | 22,590 (23) | 55.985,0 (23) | 42,0 |
| claude-haiku-5-5 | high | 24 | 32,636 (24) | 61.617,0 (24) | 43,0 |
| claude-haiku-5-5 | xhigh | 24 | 57,091 (24) | 87.451,5 (24) | 38,5 |
| claude-haiku-5-5 | max | 24 | 166,074 (24) | 195.129,5 (24) | 38,0 |
| claude-opus-5-5 | low | 24 | 20,838 (24) | 37.178,5 (24) | 38,5 |
| claude-opus-5-5 | medium | 24 | 26,472 (24) | 41.283,0 (24) | 46,0 |
| claude-opus-5-5 | high | 24 | 30,887 (24) | 42.501,0 (24) | 47,5 |
| claude-opus-5-5 | xhigh | 24 | 52,110 (24) | 53.390,5 (24) | 54,0 |
| claude-opus-5-5 | max | 21 | 348,600 (21) | 260.660,0 (21) | 48,0 |
| claude-fable-5-2 | low | 4 | 30,766 (4) | 35.199,5 (4) | 113,0 |
| claude-fable-5-2 | medium | 5 | 32,674 (5) | 34.764,0 (5) | 101,0 |
| claude-fable-5-2 | high | 6 | 39,556 (6) | 37.257,5 (6) | 26,5 |
| claude-fable-5-2 | xhigh | 5 | 173,479 (5) | 85.600,0 (5) | 27,0 |
| claude-fable-5-2 | max | 2 | 128,236 (2) | 86.655,5 (2) | 18,0 |

### Uso e interpretación de los recibos

Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.

La continuación sigue [ENMIENDA-02-02.md](../ENMIENDA-02-02.md), con aislamiento y hashes propios en protocolo-02-02. El banco y los históricos permanecen intactos. Las dos observaciones anteriores de Opus y el piloto anterior de Haiku son protocolo anterior y no están en esta matriz. La reclasificación anterior de Luna permanece documentada en ENMIENDA-02-01.md; esta continuación no reclasifica corridas históricas de Luna ni del protocolo anterior.

### Denegaciones e identidad informada por Claude

Una denegación se cuenta sin invalidar la corrida. El efectivo es el ID con más tokens de salida de modelUsage; los otros IDs con menos salida se registran como auxiliares. Fable se solicitó como claude-fable-5-2: el rótulo de sus tablas sigue al ID informado, incluso si difiere.

| Modelo solicitado | Denegaciones principales | Corridas con denegación | Modelos efectivos principales | Efectivo ausente | Auxiliares (tokens de salida) |
|---|---:|---:|---|---:|---|
| claude-haiku-5-5 | 1 | 1 | claude-haiku-5-5 | 0 | Ninguno informado |
| claude-opus-5-5 | 1 | 1 | claude-opus-5-5 | 3 | Ninguno informado |
| claude-fable-5-2 | 0 | 0 | claude-fable-5-2 | 5 | Ninguno informado |

### Protocolo anterior, fuera de esta matriz

Los archivos originales se conservan con sus hashes. Opus: dos principales (una evaluable resuelta y una anulada por la regla anterior del adaptador); Haiku: un piloto anulado por esa misma regla. Estos tres casos no se reevalúan ni se suman a la matriz nueva. Los sondeos y pilotos anteriores de los demás modelos tampoco se incorporan a los bloques nuevos. El diagnóstico nuevo de Luna está separado de todas las tablas anteriores y de sus razones.
