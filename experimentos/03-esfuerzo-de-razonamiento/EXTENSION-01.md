# Extensión 01 · esfuerzos xhigh y max

Este documento amplía el Experimento 03; no crea otro experimento. Se guarda **solo en un commit antes del piloto y de cualquier corrida nueva**. El resultado se informa como salga, sin ajustar tareas, métricas, umbrales ni repeticiones después de ver respuestas.

## Pregunta e hipótesis

Con el mismo modelo `gpt-6.1-sol`, ¿qué agregan `xhigh` y `max` frente a `low`, `medium` y `high` en aciertos, tokens, segundos y cambios fuera de alcance? La lista de esfuerzos aceptados informada para este pedido incluye `low`, `medium`, `high`, `xhigh` y `max`; no se usa `ultra`.

La hipótesis exploratoria es que los esfuerzos mayores podrían consumir más tokens y tiempo y resolver más requisitos de diseño. También pueden empatar, fallar o rendir peor. El banco original alcanzó un techo de aciertos: esta extensión conserva esa limitación y no agrega dificultad para producir diferencias.

## Contrato que no cambia

El banco congelado, los enunciados, los inicios, las referencias, los tests ocultos y `medir.py` permanecen idénticos. Antes de cualquier ejecución se compara cada hash SHA-256 de `banco-congelado.json` con los archivos actuales y se conserva evidencia pública de esa comparación. No se vuelve a generar el manifiesto.

Se mantienen Python `3.12.3`, `codex-cli 0.166.0`, modelo exacto, prompt, aislamiento, autenticación oficial, métricas y reglas de evaluación del pre-registro original. El agente dispone de **600 segundos (10 minutos)** por corrida; cada suite oculta dispone de 30 segundos. La concurrencia máxima sigue en **dos procesos de agente**, con tandas de hasta dos, esperando el cierre de cada tanda antes de lanzar la siguiente. Un suplemento importa y reutiliza el arnés congelado para preparar el orden y separar los archivos; no cambia cómo se llama, mide ni evalúa al agente.

Una corrida resuelta requiere terminar correctamente dentro del plazo y aprobar todos los tests ocultos. Los timeouts y errores se conservan tal cual ocurran, cuentan como no resueltos y no se reintentan para mejorar el resultado. Ante un error general de infraestructura se pausa la matriz según el protocolo original y se informa la cobertura real. Retomar sólo permite corridas nunca iniciadas; una iniciada sin cierre exige auditoría manual.

## Piloto y matriz fijados

- **Piloto excluido:** tarea `01-lotes`, una corrida `xhigh` y una `max`, en orden mezclado con `random.Random(2026111301).shuffle`. Sirve para verificar el funcionamiento del arnés y la aceptación de ambos niveles, no para cambiar tareas o criterios. Se conserva en `resultados/piloto-extension.csv`, con recibos aparte. No entra en ninguna tabla principal ni de control. Si el piloto no completa con uso disponible y sin errores de infraestructura, no se lanza la matriz.
- **Matriz nueva principal:** ocho tareas × dos niveles (`xhigh`, `max`) × tres repeticiones = **48 corridas**.
- **Control contemporáneo:** ocho corridas `high`, una por tarea, para observar el movimiento entre tandas. No se suman a las 24 originales de `high` en la tabla principal.
- **Orden único:** se construyen primero las 48 corridas en orden de tarea, nivel (`xhigh`, `max`) y repetición (1–3), se agregan después los ocho controles `high` en orden de tarea y se mezcla la lista completa de **56 corridas** con `random.Random(2026111301).shuffle`. La semilla nueva es fija y distinta de la original (`20261113`); sólo controla el orden, no las respuestas del modelo. La lista se guarda antes del lanzamiento.

## Archivos y análisis previstos

`resultados/crudo.csv` y los artefactos originales no se modifican. Las 56 observaciones nuevas van en `resultados/crudo-extension.csv`; piloto, inicios, recibos, métricas por corrida y módulos generados quedan separados bajo nombres de extensión. Se conservan los campos y el tratamiento de valores ausentes del protocolo original. El código suplementario se fija en Git antes del piloto.

Se agrega al final de `resultados/resumen.md` la sección **«Extensión: xhigh y max»**, conservando íntegro el texto original. La tabla por tipo muestra los cinco niveles: `low`, `medium` y `high` usan exclusivamente las 72 observaciones originales; `xhigh` y `max` usan las 48 nuevas. Por nivel y tipo se informan n, resueltas, mediana de tokens y su denominador, mediana de segundos, cambios fuera de alcance y mediana de líneas tocadas. Las medianas incluyen éxitos y fallos con datos disponibles. Se agrega el corte de resueltas y el detalle por tarea para no esconder fallos o heterogeneidad.

El control de `high` tiene una tabla propia: por tarea se compara la mediana de sus tres corridas de la tanda 1 con la única corrida de la tanda 2, incluyendo segundos y su cociente tanda 2/tanda 1, tokens y resolución. También se resumen los grupos acotada/diseño con sus denominadores explícitos. No se ajustan los tiempos de otros niveles con ese cociente ni se fusionan controles con las tres repeticiones originales. Se informan errores, timeouts, datos de uso ausentes y cobertura efectiva.

## Límite temporal y lo que este experimento no demuestra

Las corridas nuevas ocurren en otro momento que las 72 originales, con otra carga del servidor y posibles cambios remotos del proveedor aunque el identificador del modelo siga igual. Por eso la comparación de **tiempo** con `low`, `medium` y `high` es más débil que la de tokens y aciertos; estas últimas tampoco quedan libres de toda diferencia entre tandas. Los ocho controles `high`, intercalados en el mismo orden aleatorio, permiten observar cuánto se movió su tiempo. Una sola repetición de control por tarea no separa variabilidad aleatoria de cambios de carga ni elimina ese sesgo.

Se mantienen todos los límites originales: un modelo, un lenguaje, tareas artificiales, muestras pequeñas, tests parciales, líneas que no miden limpieza, tokens que no equivalen a dinero y ausencia de inferencia causal o significancia estadística. No se define ganador por diferencias pequeñas de medianas ni se extrapola a producción.

El cierre agrega una lectura de los cinco niveles y termina con **«Qué se puede decir en un reel»**: dos o tres frases sostenidas por los datos y las afirmaciones que no sostienen. Se actualiza únicamente la fila del Experimento 03 en la tabla raíz. No se hace push ni publicación.
