# Verificación final · Extensión 02

El candidato científico revisado fue `90676d488bbfc95078e54d1bbcdf45494e786c96`; el pre-registro fue `0e11257`. Una revisión independiente dirigida confirmó un **cierre parcial auditable**, sin nuevas inferencias ni cambios de resultados. La matriz completa entre modelos sigue incompleta.

La limpieza posterior de fixtures sintéticos quedó en `81fb54c694e49c2fbab51a2e7c6d9ec0b0e5ac70`: el test construye sus entradas ficticias en memoria desde fragmentos, sin persistir un correo ni una ruta personal completos. No había datos privados reales en esos fixtures. Este informe se incorpora después de ese commit para evitar referencias circulares.

## Comprobaciones

- **27/27 tests locales aprobados**, también después de la limpieza de fixtures.
- **34 hashes congelados coinciden** y los **cuatro CSV de las tandas anteriores** permanecen idénticos.
- El README raíz sólo cambia en la fila del experimento 03; el resumen histórico anterior a extensión 02 se conserva.
- **141 recibos reconciliados**: 122 principales, tres pilotos y 16 sondeos. Los CSV coinciden con los registros de corridas y sus totales con los campos crudos de uso, sin duplicar caché ni razonamiento.
- Luna conserva 120 IDs únicos y 40 celdas tarea × nivel, con tres repeticiones por celda y el orden reconstruido con semilla 2026111302.
- La reconstrucción global de intervalos confirmó **máximo dos agentes simultáneos**. El máximo principal observado fue **225,433 segundos**, inferior al tope de 600. No hubo timeouts ni cortes por cuota principales.
- Las tablas y el resumen se regeneraron **idénticos byte a byte**, sin modificar CSV. SHA-256 del resumen: `3b4cc11a1bf5ff223fc5dd686e72e91d7cfbb0aaa34e9acebf9781f17cfea854`.
- El arnés de medición no cambió con la limpieza: SHA-256 `2ce9a5e3315f465f09157ae392e370304e2d8c8d505ba99404178b5b625291a4`. La corrección anterior sigue documentada en la enmienda operativa y su registro de transición explícita; no se regeneró el congelado original.

## Resultado y cobertura

Las 122 principales nuevas contienen **121 observaciones evaluables: 110 resueltas y 11 fallos funcionales**; una observación de Opus quedó fuera del denominador funcional por el control conservador del adaptador. Los pilotos y sondeos están excluidos.

| Modelo | Cobertura y resultado |
|---|---|
| Sol, referencia | 24/24 por nivel; usa 72 originales y 48 de xhigh/max, excluyendo ocho controles high. |
| Luna | 120 principales completas: low 13/24; medium, high, xhigh y max 24/24 cada uno. Los once fallos funcionales son low y están detallados por tarea y corrida. |
| Haiku | Cero principales; 120 nunca iniciadas. El piloto tuvo retorno 0 y 3/3 tests, pero una denegación Bash de comando desconocido detuvo la validación del adaptador. |
| Opus | Dos principales observadas: una evaluable resuelta y una bloqueada por el adaptador, también con retorno 0, 3/3 tests y denegación Bash de comando desconocido. Quedaron 118 nunca iniciadas. |
| Fable | Sólo un sondeo. El recibo informa uso de `claude-fable-5-1` y `claude-opus-4-8`, sin declarar un modelo principal. Fable 5.2 no fue confirmado; no hubo piloto ni matriz y sus pendientes quedan sin definir. |

Las denegaciones de Bash **no prueban que Python permitido estuviera denegado ni incapacidad de los modelos**. No se conservó el comando arbitrario y no se adivina su naturaleza. Los cierres conservadores se informan como limitación del adaptador, sin transformarlos en fallos de programación. Tampoco se atribuye la respuesta del alias Fable a ninguno de los dos identificadores auxiliares o agregados del recibo.

## Razones verificadas desde medianas crudas

| Modelo | Tiempo max/low | Tokens max/low |
|---|---:|---:|
| Sol | 2,482665466006303466906798739 | 1,382643369597638895430069546 |
| Luna | 2,487245684340320591861898890 | 1,194071563663230764906419528 |

Los cocientes coinciden con la trazabilidad y se calcularon antes de redondear. Haiku, Opus y Fable no tienen cobertura comparable de extremos. Los totales de tokens de CLI diferentes no son homogéneos ni precios de suscripción; la referencia Sol conserva sus límites entre tandas.

## Requisitos completos y parciales

Quedaron comprobados el pre-registro separado, banco congelado, métricas y plazos, orden reproducible, concurrencia, adaptador y aislamiento documentados, uso crudo y fórmulas previas, separación de pilotos e infraestructura, bloque Luna, cierres por modelo, conservación de datos anteriores, resumen reproducible, detalle de fallos, razones comparables y límites del reel.

Permanecen parciales las matrices de Haiku y Opus y la identidad, piloto y matriz de Fable 5.2. **No se sostiene una conclusión universal**: Sol mostró techo de aciertos, mientras Luna mejoró de 13/24 con low a 24/24 con medium; los datos disponibles no permiten concluir sobre esfuerzos de Claude.

La revisión de patrones no encontró datos privados en resultados, documentación o módulos generados. La limpieza del test resuelve el hallazgo literal de fixtures ficticios persistentes; el patrón genérico del saneador permanece en el arnés fijado. Esto no es una garantía general sobre cualquier secreto textual. No hubo push ni publicación.
