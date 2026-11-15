## Extensión 02: matriz por modelo

La extensión registró **481 observaciones principales** (388 de `protocolo-02-02` + 93 de `protocolo-02-03`): 480 evaluables, con 445 resueltas y 35 fallos funcionales; 0 errores de infraestructura quedan fuera del denominador funcional. Los 5 pilotos y 25 sondeos están excluidos. Hubo 1 interrupción por cuota (en `02-02`, re-ejecutada por API en `02-03`) y 23 timeouts principales.

La referencia de gpt-6.1-sol usa 72 corridas originales y 48 de xhigh/max; excluye los ocho controles high de la extensión 01. En `claude-fable-5-2`, la fila combinada reúne las 27 corridas evaluables por suscripción (`protocolo-02-02`) y las 93 corridas por API key (`protocolo-02-03`).

«Evaluables» excluye cuota e infraestructura. Las medianas incluyen resueltas y fallos funcionales con datos disponibles; los denominadores de segundos y tokens se indican entre paréntesis.

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
| claude-fable-5-2 | low | 24/24 | 24/24 | 27,288 (24) | 32.001,0 (24) | 0/24 | 0 |
| claude-fable-5-2 | medium | 24/24 | 24/24 | 27,700 (24) | 31.586,5 (24) | 0/24 | 0 |
| claude-fable-5-2 | high | 24/24 | 24/24 | 51,568 (24) | 39.323,0 (24) | 0/24 | 0 |
| claude-fable-5-2 | xhigh | 24/24 | 24/24 | 132,604 (24) | 72.426,0 (24) | 0/24 | 0 |
| claude-fable-5-2 | max | 24/24 | 4/24 | 600,174 (24) | 124.817,5 (4) | 0/24 | 0 |

### Cobertura y cierres por bloque y canal

| Bloque | Canal | Estado | Principales observadas | Evaluables | Pendientes | Pilotos excluidos | Sondeos excluidos | Motivo |
|---|---|---|---:|---:|---:|---:|---:|---|
| gpt-6-luna | OAuth Codex | completo | 120 | 120 | 0 | 1 | 5 | Retoma sólo nunca iniciadas tras ENMIENDA-02-01 |
| claude-haiku-5-5 | OAuth Claude | completo | 120 | 120 | 0 | 1 | 5 | |
| claude-opus-5-5 | OAuth Claude | completo | 120 | 120 | 0 | 1 | 5 | |
| claude-fable-5-2 (02-02) | OAuth Claude | incompleto | 28 | 27 | 92 | 1 | 5 | cuota (1 corrida sin evaluar) |
| claude-fable-5-2 (02-03) | API key | completo | 93 | 93 | 0 | 1 | 5 | completa las 93 celdas pendientes |

### Razón nivel más alto / nivel más bajo

Los cocientes se calculan sobre las medianas de los valores crudos, antes de redondear la presentación. Sólo se informa una razón comparable cuando ambos niveles extremos tienen las 24 observaciones evaluables. Los niveles con el mismo nombre no implican igual procesamiento interno entre modelos.

Los tiempos incluyen los timeouts funcionales. Si falta el recibo final, los tokens quedan ausentes. El cociente de sus medianas usa sólo los datos disponibles, con n explícitos: no representa el consumo de las corridas sin recibo.

| Modelo | Niveles | Segundos nivel bajo (n) | Segundos nivel alto (n) | Razón tiempo | Tokens nivel bajo (n) | Tokens nivel alto (n) | Razón tokens |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-6.1-sol | max/low | 41,088 (24) | 102,009 (24) | 2,483 | 95.548,5 (24) | 132.109,5 (24) | 1,383 |
| gpt-6-luna | max/low | 38,928 (24) | 96,824 (24) | 2,487 | 124.518,5 (24) | 148.684,0 (24) | 1,194 |
| claude-haiku-5-5 | max/low | 18,553 (24) | 166,074 (24) | 8,951 | 47.353,0 (24) | 195.129,5 (24) | 4,121 |
| claude-opus-5-5 | max/low | 20,838 (24) | 376,156 (24) | 18,051 | 37.178,5 (24) | 260.660,0 (21) | 7,011 (datos parciales) |
| claude-fable-5-2 | max/low | 27,288 (24) | 600,174 (24) | 21,994 | 32.001,0 (24) | 124.817,5 (4) | 3,900 (datos parciales) |

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
| claude-fable-5-2 | 02-intervalos | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| claude-fable-5-2 | 03-importes | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| claude-fable-5-2 | 04-espera | 3/3 | 3/3 | 3/3 | 3/3 | 1/3 |
| claude-fable-5-2 | 05-consulta | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| claude-fable-5-2 | 06-inventario | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| claude-fable-5-2 | 07-planificador | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |
| claude-fable-5-2 | 08-cache | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 |

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
| claude-fable-5-2 | principal-07-planificador-max-2 | 0/1 | 600.484 | — | timeout_agente |
| claude-fable-5-2 | principal-03-importes-max-1 | 0/2 | 600.688 | — | timeout_agente |
| claude-fable-5-2 | principal-07-planificador-max-3 | 5/5 | 600.193 | — | timeout_agente |
| claude-fable-5-2 | principal-03-importes-max-2 | 2/2 | 600.194 | — | timeout_agente |
| claude-fable-5-2 | principal-06-inventario-max-3 | 0/1 | 600.193 | — | timeout_agente |
| claude-fable-5-2 | principal-02-intervalos-max-2 | 3/3 | 600.199 | — | timeout_agente |
| claude-fable-5-2 | principal-06-inventario-max-2 | 5/5 | 600.159 | — | timeout_agente |
| claude-fable-5-2 | principal-05-consulta-max-1 | 3/3 | 600.172 | — | timeout_agente |
| claude-fable-5-2 | principal-02-intervalos-max-3 | 3/3 | 600.181 | — | timeout_agente |
| claude-fable-5-2 | principal-06-inventario-max-1 | 5/5 | 600.153 | — | timeout_agente |
| claude-fable-5-2 | principal-03-importes-max-3 | 2/2 | 600.175 | — | timeout_agente |
| claude-fable-5-2 | principal-08-cache-max-1 | 6/6 | 600.176 | — | timeout_agente |
| claude-fable-5-2 | principal-04-espera-max-1 | 2/2 | 600.15 | — | timeout_agente |
| claude-fable-5-2 | principal-08-cache-max-3 | 6/6 | 600.179 | — | timeout_agente |
| claude-fable-5-2 | principal-07-planificador-max-1 | 5/5 | 600.169 | — | timeout_agente |

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
| claude-fable-5-2 | low | 24 | 27,288 (24) | 32.001,0 (24) | 46,0 |
| claude-fable-5-2 | medium | 24 | 27,700 (24) | 31.586,5 (24) | 44,5 |
| claude-fable-5-2 | high | 24 | 51,568 (24) | 39.323,0 (24) | 53,5 |
| claude-fable-5-2 | xhigh | 24 | 132,604 (24) | 72.426,0 (24) | 54,0 |
| claude-fable-5-2 | max | 4 | 202,211 (4) | 124.817,5 (4) | 18,0 |

### Uso e interpretación de los recibos

Codex: total = input_tokens + output_tokens; su caché y razonamiento no se suman otra vez. Claude: total = input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens; no se suman los desgloses de thinking ni modelUsage encima de usage. Los recibos numéricos crudos conservan ambas contabilidades, duración y turnos cuando el CLI los entrega. La comparación de tokens válida es entre niveles de un mismo modelo y CLI; los totales entre CLI no son homogéneos ni representan precios de suscripción.

La continuación inicial sigue [ENMIENDA-02-02.md](../ENMIENDA-02-02.md) (`protocolo-02-02`); el completado de Fable por API key sigue [ENMIENDA-02-03.md](../ENMIENDA-02-03.md) (`protocolo-02-03`), preservando intactos los datos históricos y de `protocolo-02-02`.

### Denegaciones e identidad informada por Claude

Una denegación se cuenta sin invalidar la corrida. El efectivo es el ID con más tokens de salida de modelUsage; los otros IDs con menos salida se registran como auxiliares.

| Modelo solicitado | Denegaciones principales | Corridas con denegación | Modelos efectivos principales | Efectivo ausente | Auxiliares (tokens de salida) |
|---|---:|---:|---|---:|---|
| claude-haiku-5-5 | 1 | 1 | claude-haiku-5-5 | 0 | Ninguno informado |
| claude-opus-5-5 | 1 | 1 | claude-opus-5-5 | 3 | Ninguno informado |
| claude-fable-5-2 | 0 | 0 | claude-fable-5-2 | 20 | Ninguno informado |

### Protocolo anterior, fuera de esta matriz

Los archivos originales se conservan con sus hashes. Opus: dos principales (una evaluable resuelta y una anulada por la regla anterior del adaptador); Haiku: un piloto anulado por esa misma regla. Estos tres casos no se reevalúan ni se suman a la matriz nueva. El diagnóstico nuevo de Luna está separado de todas las tablas anteriores y de sus razones.
