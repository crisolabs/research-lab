# Resultados · esfuerzo de razonamiento

Cobertura: **72/72 corridas principales**, realizadas el 13 de noviembre de 2026. Piloto de tres corridas excluido. Modelo `gpt-6.1-sol`, CLI `0.166.0`, Python `3.12.3`; semilla de orden 20261113, tres repeticiones por tarea y nivel, dos agentes simultáneos como máximo. No hubo errores del CLI, timeouts ni datos de uso ausentes. El pre-registro es el commit `e22569c`, el banco congelado `3bf43bd` y el piloto separado `407d844`.

| Tipo | Nivel | n | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |
|---|---|---:|---:|---:|---:|---:|---:|
| acotada | low | 15 | 15/15 (100.0 %) | 92815.0 (15) | 33.8 | 0/15 (0.0 %) | 22.0 |
| acotada | medium | 15 | 15/15 (100.0 %) | 93205.0 (15) | 40.1 | 0/15 (0.0 %) | 18.0 |
| acotada | high | 15 | 15/15 (100.0 %) | 113517.0 (15) | 55.2 | 0/15 (0.0 %) | 18.0 |
| diseño | low | 9 | 9/9 (100.0 %) | 101008.0 (9) | 49.0 | 0/9 (0.0 %) | 88.0 |
| diseño | medium | 9 | 9/9 (100.0 %) | 102288.0 (9) | 56.4 | 0/9 (0.0 %) | 93.0 |
| diseño | high | 9 | 9/9 (100.0 %) | 133571.0 (9) | 79.2 | 0/9 (0.0 %) | 97.0 |

## Respuesta

Los tres niveles resolvieron todas las tareas de esta muestra: **24/24 por nivel**, sin archivos modificados fuera de los módulos permitidos. Ese resultado tiene un efecto techo: el banco no distingue mejoras de corrección por encima del 100 %. No demuestra que el razonamiento no sirva; estas tareas no exigieron una diferencia observable en los tests.

`high` tardó más que `medium` en las medianas de las ocho tareas. En los cambios acotados, la mediana fue 55,164 frente a 40,141 segundos (**1,37 veces**); en diseño, 79,191 frente a 56,395 segundos (**1,40 veces**). Los tokens totales medianos también fueron mayores con `high` en siete de las ocho tareas. Es un patrón descriptivo consistente en este banco; tres repeticiones por tarea no fijan cuánto cambia el rendimiento en otros trabajos.

La comparación `low`–`medium` es menos clara: `medium` fue más lento en seis de las ocho medianas por tarea, pero las medianas de tokens de cambios acotados quedaron cerca (92.815 y 93.205). En dos tareas `medium` tuvo una mediana de tiempo levemente menor que `low`. Ningún nivel ganó en resolución o cambios fuera de alcance: todos quedaron empatados en esas métricas. Las líneas tocadas tampoco miden limpieza: en acotadas las medianas fueron 22, 18 y 18; en diseño, 88, 93 y 97 para low, medium y high.

Las tablas incluyen las 72 corridas, sin seleccionar sólo resultados favorables. El corte de resueltas es idéntico porque todas aprobaron. El [CSV crudo](crudo.csv), el [piloto excluido](piloto.csv), los [recibos del CLI](recibos/) y los [módulos generados](codigo/) permiten revisar cada observación.

## Sólo corridas resueltas

| Tipo | Nivel | n | Tokens mediana | Segundos mediana | Líneas mediana |
|---|---|---:|---:|---:|---:|
| acotada | low | 15 | 92815.0 | 33.8 | 22.0 |
| acotada | medium | 15 | 93205.0 | 40.1 | 18.0 |
| acotada | high | 15 | 113517.0 | 55.2 | 18.0 |
| diseño | low | 9 | 101008.0 | 49.0 | 88.0 |
| diseño | medium | 9 | 102288.0 | 56.4 | 93.0 |
| diseño | high | 9 | 133571.0 | 79.2 | 97.0 |

## Por tarea

| Tarea | Nivel | Resueltas | Tokens mediana | Segundos mediana |
|---|---|---:|---:|---:|
| 01-lotes | low | 3/3 | 84226.0 | 28.6 |
| 01-lotes | medium | 3/3 | 85663.0 | 28.3 |
| 01-lotes | high | 3/3 | 83958.0 | 32.2 |
| 02-intervalos | low | 3/3 | 84401.0 | 33.7 |
| 02-intervalos | medium | 3/3 | 93205.0 | 41.8 |
| 02-intervalos | high | 3/3 | 116020.0 | 55.2 |
| 03-importes | low | 3/3 | 99445.0 | 40.3 |
| 03-importes | medium | 3/3 | 99500.0 | 40.0 |
| 03-importes | high | 3/3 | 115321.0 | 57.8 |
| 04-espera | low | 3/3 | 92815.0 | 57.8 |
| 04-espera | medium | 3/3 | 115875.0 | 64.6 |
| 04-espera | high | 3/3 | 140343.0 | 92.6 |
| 05-consulta | low | 3/3 | 99435.0 | 31.7 |
| 05-consulta | medium | 3/3 | 83903.0 | 32.7 |
| 05-consulta | high | 3/3 | 113517.0 | 41.3 |
| 06-inventario | low | 3/3 | 89850.0 | 52.8 |
| 06-inventario | medium | 3/3 | 119635.0 | 62.6 |
| 06-inventario | high | 3/3 | 140405.0 | 86.9 |
| 07-planificador | low | 3/3 | 101479.0 | 49.0 |
| 07-planificador | medium | 3/3 | 90021.0 | 56.4 |
| 07-planificador | high | 3/3 | 133571.0 | 87.9 |
| 08-cache | low | 3/3 | 101008.0 | 42.8 |
| 08-cache | medium | 3/3 | 102288.0 | 50.9 |
| 08-cache | high | 3/3 | 120182.0 | 78.1 |

## Tokens informados por el CLI

| Nivel | n | Entrada mediana | Entrada en caché mediana | Salida mediana | Razonamiento mediana | Total mediana |
|---|---:|---:|---:|---:|---:|---:|
| low | 24 | 94.546,5 | 88.128,0 | 1.119,0 | 65,0 | 95.548,5 |
| medium | 24 | 98.644,0 | 91.968,0 | 1.270,5 | 150,0 | 99.625,0 |
| high | 24 | 116.250,5 | 110.400,0 | 2.050,5 | 373,0 | 118.101,0 |

El CLI entregó `input_tokens`, `cached_input_tokens`, `output_tokens` y `reasoning_output_tokens` en las 72 corridas. El total pre-registrado es entrada + salida; la caché está contenida en la entrada y no se suma otra vez. El razonamiento se conserva tal como lo informa el CLI y no se vuelve a sumar al total. Un cero en ese campo es el valor del recibo; no prueba ausencia de procesamiento interno.

La entrada incluye contexto reutilizado entre llamadas y herramientas de una misma corrida. Por eso el total no equivale al tamaño del enunciado. La suma de tokens del CLI no equivale al precio de una llamada: caché, tarifas y modalidad de acceso pueden cambiar el costo. No se midieron importes monetarios.

## Tamaño real del banco y desviaciones

| Tarea | Tipo fijado | Líneas físicas de referencia | Líneas cambiadas de referencia respecto al inicio |
|---|---|---:|---:|
| 01-lotes | acotada | 11 | 10 |
| 02-intervalos | acotada | 17 | 16 |
| 03-importes | acotada | 12 | 11 |
| 04-espera | acotada | 15 | 14 |
| 05-consulta | acotada | 8 | 3 |
| 06-inventario | diseño | 85 | 85 |
| 07-planificador | diseño | 73 | 73 |
| 08-cache | diseño | 68 | 68 |

Para esta tabla, un bloque reemplazado cuenta el máximo entre líneas borradas y agregadas; no es la métrica principal de líneas tocadas, que suma ambas. La orientación original fue aproximadamente diez líneas por cambio acotado y 80–150 por módulo de diseño. Las referencias acotadas cambiaron 10, 16, 11, 14 y 3 líneas: intervalos y espera superan esa orientación. Dos referencias de diseño tienen 73 y 68 líneas físicas y quedan por debajo. Se conservó la clasificación fijada, sin reubicar tareas después de ver resultados ni agregar relleno. Estas desviaciones limitan la comparación con la frase “cambios de diez líneas”.

## Validación final y pendientes

La revisión independiente volvió a evaluar los 72 módulos guardados con los tests ocultos: todos pasaron. También verificó los seis tests locales del arnés, los 34 hashes del banco congelado, la concordancia de los 75 recibos (72 principales y tres del piloto), las medianas, la separación del piloto y la ausencia de datos privados en los archivos del experimento. El máximo medido fue 131,884 segundos, por debajo del tope de 600, y la concurrencia no superó dos agentes.

No quedan corridas ni validaciones pendientes dentro de este protocolo. Los resultados se guardan mediante commits locales; no se hizo push ni publicación. Repetir con otros modelos, lenguajes o tareas más grandes sería otro experimento, con un nuevo pre-registro.

## Lo que este experimento no demuestra

Un único modelo, versión de CLI, lenguaje y banco artificial, con tres repeticiones por tarea y nivel, no permite generalizar a producción. High no es el esfuerzo máximo. Los tests no miden limpieza de código; los tokens no son importes monetarios. La semilla fija el orden, no las respuestas del modelo. El tiempo incluye carga y esperas del CLI. Los valores ausentes no cuentan como cero.

## Qué se puede decir en un reel

En este banco de Python, los tres niveles resolvieron las 72 corridas sin cambios fuera de alcance; el razonamiento alto no mejoró los aciertos observados. High tuvo una mediana de tiempo 1,37 veces la de Medium en cambios acotados y 1,40 veces en diseño, con más tokens medianos en siete de las ocho tareas. Estos datos no sostienen que Medium produzca “el 90 % del código más limpio” ni una regla general del triple de tiempo: no medimos limpieza ni el esfuerzo máximo, y no podemos extender el resultado a otros modelos o tareas.

## Extensión: xhigh y max

Cobertura nueva: **56/56 corridas**: 48/48 principales y 8/8 controles high. Piloto de dos corridas excluido. Semilla 2026111301; mismo banco, arnés y límites que la tanda original. El pre-registro de esta extensión se encuentra en [EXTENSION-01.md](../EXTENSION-01.md).

La tabla conserva low, medium y high de la tanda 1 (24 corridas por nivel) y agrega xhigh y max de la tanda 2 (24 por nivel si la cobertura está completa). Los controles high nuevos se analizan por separado. Las medianas incluyen corridas exitosas y fallidas con datos disponibles; un uso ausente no equivale a cero.

| Tipo | Nivel | n | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |
|---|---|---:|---:|---:|---:|---:|---:|
| acotada | low | 15 | 15/15 (100.0 %) | 92815.0 (15) | 33.8 | 0/15 (0.0 %) | 22.0 |
| acotada | medium | 15 | 15/15 (100.0 %) | 93205.0 (15) | 40.1 | 0/15 (0.0 %) | 18.0 |
| acotada | high | 15 | 15/15 (100.0 %) | 113517.0 (15) | 55.2 | 0/15 (0.0 %) | 18.0 |
| acotada | xhigh | 15 | 15/15 (100.0 %) | 130263.0 (15) | 75.8 | 0/15 (0.0 %) | 20.0 |
| acotada | max | 15 | 15/15 (100.0 %) | 130388.0 (15) | 91.4 | 0/15 (0.0 %) | 18.0 |
| diseño | low | 9 | 9/9 (100.0 %) | 101008.0 (9) | 49.0 | 0/9 (0.0 %) | 88.0 |
| diseño | medium | 9 | 9/9 (100.0 %) | 102288.0 (9) | 56.4 | 0/9 (0.0 %) | 93.0 |
| diseño | high | 9 | 9/9 (100.0 %) | 133571.0 (9) | 79.2 | 0/9 (0.0 %) | 97.0 |
| diseño | xhigh | 9 | 9/9 (100.0 %) | 140699.0 (9) | 131.6 | 0/9 (0.0 %) | 106.0 |
| diseño | max | 9 | 9/9 (100.0 %) | 149146.0 (9) | 161.4 | 0/9 (0.0 %) | 100.0 |

### Control de high: tanda 1 frente a tanda 2

La tanda 1 aporta tres repeticiones por tarea; la tanda 2 aporta una por tarea, intercalada con xhigh y max. Los cocientes son descriptivos y no corrigen los tiempos de otros niveles.

| Tarea | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Segundos tanda 1 | Segundos tanda 2 | Cociente 2/1 | Tokens tanda 1 | Tokens tanda 2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01-lotes | 3 / 1 | 3/3 / 1/1 | 32.2 | 43.0 | 1.33 | 83958.0 | 99003.0 |
| 02-intervalos | 3 / 1 | 3/3 / 1/1 | 55.2 | 42.9 | 0.78 | 116020.0 | 100064.0 |
| 03-importes | 3 / 1 | 3/3 / 1/1 | 57.8 | 61.2 | 1.06 | 115321.0 | 115078.0 |
| 04-espera | 3 / 1 | 3/3 / 1/1 | 92.6 | 113.9 | 1.23 | 140343.0 | 139620.0 |
| 05-consulta | 3 / 1 | 3/3 / 1/1 | 41.3 | 40.0 | 0.97 | 113517.0 | 99458.0 |
| 06-inventario | 3 / 1 | 3/3 / 1/1 | 86.9 | 109.9 | 1.27 | 140405.0 | 122603.0 |
| 07-planificador | 3 / 1 | 3/3 / 1/1 | 87.9 | 87.2 | 0.99 | 133571.0 | 119912.0 |
| 08-cache | 3 / 1 | 3/3 / 1/1 | 78.1 | 67.3 | 0.86 | 120182.0 | 132237.0 |

| Tipo | n tanda 1 / tanda 2 | Resueltas tanda 1 / tanda 2 | Tokens tanda 1 (n) | Tokens tanda 2 (n) | Segundos tanda 1 | Segundos tanda 2 | Fuera de alcance tanda 1 / tanda 2 | Líneas tanda 1 / tanda 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| acotada | 15 / 5 | 15/15 / 5/5 | 113517.0 (15) | 100064.0 (5) | 55.2 | 43.0 | 0/15 / 0/5 | 18.0 / 17.0 |
| diseño | 9 / 3 | 9/9 / 3/3 | 133571.0 (9) | 122603.0 (3) | 79.2 | 87.2 | 0/9 / 0/3 | 97.0 / 92.0 |

### Sólo corridas resueltas: cinco niveles

| Tipo | Nivel | n | Tokens mediana | Segundos mediana | Líneas mediana |
|---|---|---:|---:|---:|---:|
| acotada | low | 15 | 92815.0 | 33.8 | 22.0 |
| acotada | medium | 15 | 93205.0 | 40.1 | 18.0 |
| acotada | high | 15 | 113517.0 | 55.2 | 18.0 |
| acotada | xhigh | 15 | 130263.0 | 75.8 | 20.0 |
| acotada | max | 15 | 130388.0 | 91.4 | 18.0 |
| diseño | low | 9 | 101008.0 | 49.0 | 88.0 |
| diseño | medium | 9 | 102288.0 | 56.4 | 93.0 |
| diseño | high | 9 | 133571.0 | 79.2 | 97.0 |
| diseño | xhigh | 9 | 140699.0 | 131.6 | 106.0 |
| diseño | max | 9 | 149146.0 | 161.4 | 100.0 |

### Por tarea: nuevos niveles

| Tarea | Nivel | Resueltas | Tokens mediana (n) | Segundos mediana | Fuera de alcance | Líneas mediana |
|---|---|---:|---:|---:|---:|---:|
| 01-lotes | xhigh | 3/3 | 129784.0 (3) | 54.7 | 0/3 | 15.0 |
| 01-lotes | max | 3/3 | 115713.0 (3) | 55.8 | 0/3 | 15.0 |
| 02-intervalos | xhigh | 3/3 | 119010.0 (3) | 75.8 | 0/3 | 35.0 |
| 02-intervalos | max | 3/3 | 133831.0 (3) | 95.0 | 0/3 | 34.0 |
| 03-importes | xhigh | 3/3 | 132461.0 (3) | 95.2 | 0/3 | 20.0 |
| 03-importes | max | 3/3 | 134002.0 (3) | 94.0 | 0/3 | 18.0 |
| 04-espera | xhigh | 3/3 | 184496.0 (3) | 205.1 | 0/3 | 35.0 |
| 04-espera | max | 3/3 | 155096.0 (3) | 180.9 | 0/3 | 32.0 |
| 05-consulta | xhigh | 3/3 | 100896.0 (3) | 60.8 | 0/3 | 10.0 |
| 05-consulta | max | 3/3 | 119135.0 (3) | 70.7 | 0/3 | 10.0 |
| 06-inventario | xhigh | 3/3 | 147069.0 (3) | 138.0 | 0/3 | 116.0 |
| 06-inventario | max | 3/3 | 157093.0 (3) | 191.4 | 0/3 | 100.0 |
| 07-planificador | xhigh | 3/3 | 171684.0 (3) | 149.7 | 0/3 | 108.0 |
| 07-planificador | max | 3/3 | 149146.0 (3) | 161.4 | 0/3 | 107.0 |
| 08-cache | xhigh | 3/3 | 108774.0 (3) | 97.2 | 0/3 | 79.0 |
| 08-cache | max | 3/3 | 111066.0 (3) | 106.7 | 0/3 | 83.0 |

### Errores, timeouts y uso ausente

Corridas nuevas: 0 timeouts de agente, 0 errores del CLI, 0 timeouts de tests, 0 recibos sin tokens totales y 0 corridas no resueltas. No se reintentaron observaciones.

### Lectura de los cinco niveles

Los cinco niveles resolvieron **24/24 corridas por nivel**: 120 principales en total, sin cambios fuera de alcance. Los ocho controles nuevos de high también pasaron; el piloto de dos corridas quedó excluido y pasó completo. Xhigh y max no agregaron aciertos observables frente a los niveles originales. El banco conserva el efecto techo: este empate no demuestra que el esfuerzo de razonamiento sea inútil en otras tareas.

Las medianas agregadas de tiempo y tokens aumentaron al recorrer los cinco niveles. En cambios acotados, xhigh y max tuvieron medianas de 75,8 y 91,4 segundos; en diseño, 131,6 y 161,4. Los tokens medianos de xhigh y max quedaron casi empatados en acotadas (130.263 y 130.388), mientras que en diseño fueron 140.699 y 149.146. El patrón agregado no se cumple en cada tarea: max usó menos tokens medianos que xhigh en lotes, espera y planificador, y fue más rápido en importes y espera. Las medianas de líneas tampoco avanzaron de manera uniforme; ninguna de esas diferencias mide limpieza de código.

El control high mostró movimientos en ambas direcciones. Su mediana en acotadas pasó de 55,2 a 43,0 segundos (15 frente a cinco observaciones), y en diseño de 79,2 a 87,2 (nueve frente a tres). Los cocientes por tarea de la segunda tanda respecto de la primera van aproximadamente de 0,78 a 1,33. Una única corrida nueva por tarea mezcla variación de respuestas, herramientas, esperas y carga; no demuestra qué proporción del cambio proviene del servidor. Por eso no usamos ese control para normalizar ni corregir los tiempos.

Max tuvo una mediana de tiempo 2,28 veces la de medium en cambios acotados y 2,86 veces en diseño. Esos cocientes describen estas observaciones, realizadas en tandas distintas; no estiman un efecto aislado del nivel ni sostienen una regla general del triple. La comparación de tiempo con low, medium y high originales es más débil que la de tokens y aciertos. También los tokens de high cambiaron entre tandas: la mediana de acotadas pasó de 113.517 a 100.064 y la de diseño de 133.571 a 122.603. El control pequeño no permite separar cambios remotos del proveedor de variación de respuestas.

### Comprobaciones y artefactos de la extensión

El pre-registro quedó solo en el commit `b267ab7`, antes de las respuestas nuevas; el suplemento se fijó en `488a16c`, antes del piloto. Los 34 hashes originales siguieron coincidiendo antes del piloto y de la matriz, y el CSV original permaneció idéntico. Las 56 corridas nuevas y las dos del piloto tienen recibos separados; no se reintentó ninguna. La corrida nueva más larga duró 263,260 segundos, por debajo de 600, y los inicios registrados no superaron dos agentes simultáneos. Los nueve tests locales del arnés original y del suplemento pasaron. El inicio real de una pareja se invirtió dentro de su tanda: la corrida de orden previsto 32 (control high de planificador) comenzó 26 milisegundos antes que la 31 (intervalos/max, repetición 3). La cola prevista y las tandas se conservaron; ambos inicios reales quedaron registrados, sin reordenar observaciones ni repetirlas.

El [CSV nuevo](crudo-extension.csv) distingue las 48 principales por los niveles xhigh/max y los ocho controles por high e identificadores con `control`. El [piloto excluido](piloto-extension.csv), el [orden completo](orden-extension.json), los [recibos nuevos](extension-01/recibos/), los [módulos nuevos](extension-01/codigo/) y la [comprobación del congelado](extension-01/verificacion-congelado.json) permiten revisar cada observación. `python3 extension.py resumir` recalcula las tablas y conserva esta lectura, sin reescribir el texto original del resumen.

### Lo que este experimento no demuestra

La extensión conserva las limitaciones originales: un modelo, una versión del CLI, Python, tareas artificiales y tres repeticiones por tarea y nivel. Los tests son evidencia funcional parcial y no prueban ausencia de errores. Los controles high tienen una sola repetición nueva por tarea y no eliminan la diferencia temporal entre tandas. No se midieron dinero, limpieza, calidad de mantenimiento ni un porcentaje del código; la semilla fija el orden, no las respuestas. El resultado no se puede trasladar sin más a otros modelos, tareas, repositorios o producción.

### Qué se puede decir en un reel

En este banco, cada uno de los cinco niveles resolvió 24 de 24 corridas, y los ocho controles high también pasaron, sin cambios fuera de alcance. Max tuvo medianas de 91,4 segundos en cambios acotados y 161,4 en diseño, frente a 40,1 y 56,4 de medium; la comparación corresponde a tandas distintas y el control high mostró variaciones entre tareas. Estos datos no muestran más aciertos con xhigh o max, no sostienen una regla general del triple de tiempo y no miden el “90 % del código más limpio”.

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

### Lectura: ¿se repite el patrón en todos los modelos?

**No se sostiene una regla universal.** La referencia de `gpt-6.1-sol` conserva 24/24 resueltas en cada nivel. `gpt-6-luna` pasó de **13/24 con low a 24/24 con medium, high, xhigh y max**: aumentar el esfuerzo desde low sí agregó once aciertos observados. Aumentarlo desde medium no agregó otros aciertos en este banco. Las corridas originales de ambos modelos permanecen intactas.

**Haiku completó 120 observaciones y resolvió 119.** Low, high, xhigh y max dieron 24/24; medium, 23/24. El fallo fue `07-planificador/medium/3`, con 4/5 tests aprobados. Max tuvo una mediana de tiempo **8,951 veces** la de low y una mediana de tokens **4,121 veces**, sin agregar aciertos frente a low. El retroceso aislado de medium impide presentar los aciertos como una subida uniforme; tres repeticiones por celda no establecen una probabilidad general.

**Opus completó 120 observaciones y resolvió 117 dentro del plazo.** Low, medium, high y xhigh dieron 24/24; max, 21/24. Las otras tres de max fueron timeouts de 600 segundos: dos en `07-planificador` y uno en `02-intervalos`. Las tres pasaron todos los tests al evaluar los archivos que dejaron, pero el criterio pre-registrado exige terminar dentro del plazo; siguen como no resueltas. La mediana de tiempo max/low fue **18,051 veces**, incluyendo esos tres timeouts. La razón de tokens fue **7,011 veces sobre los recibos disponibles**: low tiene 24 datos y max 21. Ese cociente no estima los tokens de las tres corridas sin cierre ni el consumo de todas las observaciones max.

**Fable completó las 120 celdas evaluables en dos tandas declaradas (27 por suscripción bajo `protocolo-02-02` + 93 por API key bajo `protocolo-02-03`) y resolvió 100.** Low, medium, high y xhigh dieron **24/24** cada uno; **max cayó a 4/24**, con **20 timeouts de 600 segundos** (5 en `02-02` y 15 en `02-03`). De esas 20 corridas vencidas por plazo, 15 dejaron archivos que pasaron los tests ocultos y 5 no los pasaron, pero todas cuentan como no resueltas según el criterio pre-registrado de terminar dentro de los 600 s. La mediana de tiempo max/low fue **21,994 veces** (600,175 s frente a 27,288 s), y la razón de tokens max/low quedó en **3,900 veces sobre datos muy parciales de max** (`n = 4` recibos completos frente a `24` en low, excluyendo los 20 timeouts sin recibo final). Todas las identidades principales observadas coinciden con `claude-fable-5-2`.

La observación original de cuota de Fable en `02-02` (`principal-07-planificador-xhigh-2`) permanece documentada y sin cambios en [auditoria-cuota](extension-02/protocolo-02-02/fable/auditoria-cuota/correccion.json); su celda fue ejecutada y evaluada por primera vez en `02-03` mediante `ANTHROPIC_API_KEY`. El cambio de canal de autenticación/facturación entre las primeras 27 evaluables (OAuth de suscripción) y las 93 restantes (API key) queda declarado en [ENMIENDA-02-03.md](../ENMIENDA-02-03.md); los tiempos incluyen latencia de red del canal respectivo.

Las nuevas matrices de Haiku y Opus tuvieron una denegación de herramienta cada una; Fable tuvo cero denegaciones en `02-02` y cero en `02-03`. Los dos principales anteriores de Opus y el piloto anterior de Haiku conservan su clasificación como **protocolo anterior**, fuera de la matriz.

Las razones max/low de Sol y Luna se mantienen: **2,483 y 2,487 en tiempo; 1,383 y 1,194 en tokens**, respectivamente. En Luna el tiempo y los tokens tampoco aumentaron en cada escalón: xhigh tuvo medianas mayores que max. Las diferencias entre modelos mezclan proveedor, CLI, canal de autenticación, herramientas, contexto, momento y carga del host; describen estas tandas y no aíslan un efecto causal del modelo.

### Diagnóstico separado de Luna low

Las [seis corridas nuevas de diagnóstico](extension-02/diagnostico-luna-low/resumen.md) quedaron fuera de la matriz y de todas sus medianas y razones. El agente resolvió dos y dejó cuatro con **cero líneas cambiadas**. Los cuatro fallos registraron comandos de lectura con retorno 127 y mensajes finales que reconocen que no pudieron leer `TAREA.md` o avanzar. No anunciaron una implementación terminada ni presentaron un parche en texto; tampoco registraron intentos de aplicar cambios. Algunos mensajes piden compartir el contenido o habilitar una herramienta de lectura. Los tokens de salida informados de esos cuatro casos fueron 358–536; incluyen más que el mensaje final.

Las dos corridas resueltas también encontraron comandos con retorno 127. En lotes/1 el agente continuó con herramientas internas de Bash para leer archivos; en caché/2 leyó con `rg`, una herramienta de búsqueda de texto, y aplicó cambios. La evidencia distingue abandonar ante herramientas fallidas de encontrar otra vía para resolver. Que un mensaje diga que los comandos “no están instalados” es la interpretación del agente: el registro conserva comando, estado y retorno, no una auditoría de instalación ni las salidas arbitrarias de esas herramientas.

El diagnóstico revela una interacción con el entorno de herramientas que limita atribuir los fallos a una dificultad de programación o a un efecto puro del esfuerzo. No reconstruye las transcripciones de las once corridas originales que fallaron ni demuestra su causa individual. Ninguna corrida original de Luna se reclasificó. No se reparó el entorno ni se hicieron corridas adicionales. Los mensajes finales completos y las listas de comandos saneadas están en los recibos individuales; [nota.md](extension-02/diagnostico-luna-low/nota.md) contiene diez líneas de lectura.

### Comprobación y reproducción

La [enmienda 02-02](../ENMIENDA-02-02.md) se guardó sola en `0ad8fcd`; la [enmienda 02-03](../ENMIENDA-02-03.md) se guardó sola en `0a7ee11` antes de los sondeos y corridas por API de Fable. El banco conserva sus 34 hashes y los 584 archivos históricos siguen idénticos. `extension0202.py` (`863dfe5`) y todos los artefactos de `protocolo-02-02/` permanecen intactos. `extension0203.py` (`104633d`) corrió los cinco sondeos triviales, un piloto excluido y las 93 celdas pendientes de Fable sin tocar archivos de `02-02`. No se hizo push.

`python3 resumir0203.py` recalcula tablas y razones desde los CSV originales de Sol y Luna, los CSV de Haiku, Opus y la tanda inicial de Fable (`-02-02.csv`) y el CSV por API de Fable (`crudo-fable-02-03.csv`); no llama modelos ni escribe datos crudos. La trazabilidad queda en [protocolo-02-03/resumen-trazabilidad.json](extension-02/protocolo-02-03/resumen-trazabilidad.json).

### Lo que este experimento no demuestra

Estas tareas artificiales de Python, tres repeticiones por celda y los tests parciales no representan producción, repositorios grandes, limpieza ni mantenimiento del código. Aceptar el parámetro no demuestra el procesamiento interno del razonamiento; los nombres de los niveles no homologan modelos. La semilla fija el orden, no las respuestas. Las tandas ocurren en momentos distintos, en un host compartido y, en el caso de Fable, combinan dos canales de acceso (27 evaluables por suscripción y 93 por API key). Los CLI y su entorno de herramientas difieren, y las instrucciones globales de Codex siguen siendo un límite declarado; el diagnóstico refuerza ese confusor. Los tokens tienen contabilidades distintas entre CLI, no son dinero ni precios de suscripción. Los timeouts sin recibo dejan tokens e identidad ausentes. El diagnóstico exploratorio no permite corregir ni explicar individualmente los once fallos históricos de Luna.

### Qué se puede decir en un reel

En este banco de cinco modelos completos (120 corridas por modelo), el nivel útil dependió del modelo: Luna pasó de 13/24 en `low` a 24/24 desde `medium`; Haiku resolvió 119/120 pero en `max` tardó 8,95 veces más que en `low` sin sumar aciertos; Opus cayó de 24/24 a 21/24 en `max` por timeouts y tardó 18,05 veces más; y Fable 5.2 resolvió 24/24 de `low` a `xhigh`, pero en `max` cayó a 4/24 con 20 timeouts de 600 segundos (21,99 veces más tiempo mediano). Estos datos no sostienen una regla universal ni miden calidad o “90 % del código más limpio”, pero sí muestran que subir al máximo puede multiplicar tiempos y tokens —o hacer vencer el plazo— sin sumar aciertos.
