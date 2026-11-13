# Experimento 03 · ¿Más razonamiento hace que el agente programe mejor?

Este documento es el **pre-registro**: se guarda en un commit propio antes de ejecutar tests, piloto o mediciones. El banco y el arnés se congelan en otro commit antes del piloto. No se cambian tareas, métricas ni criterios después de observar respuestas del modelo.

## Pregunta e hipótesis

Con el mismo modelo (`gpt-6.1-sol`), las mismas tareas y el mismo CLI, ¿qué cambia entre esfuerzo de razonamiento `low`, `medium` y `high` en resolución, tokens, segundos y cambios fuera de lo pedido?

Un reel afirmaba que el razonamiento máximo tardaba el triple y que con Medium el 90 % del código salía más rápido y más limpio. Esa afirmación no tenía una medición detrás. **Este experimento no parte de darla por cierta.** Además, `high` no equivale necesariamente al máximo del modelo.

Hipótesis exploratorias: en cambios acotados, `medium` podría resolver tantas tareas como `high` con menos tokens y tiempo; en tareas de diseño, `high` podría resolver más. `low` podría usar menos recursos y cometer más errores. Se informan resultados contrarios y empates. No hay un umbral de éxito comercial ni se intenta confirmar el 90 %.

## Banco fijado antes de correr

Cada tarea tiene `inicio/`, `TAREA.md`, `ocultos/` y `referencia/`. El agente recibe únicamente `inicio/` y `TAREA.md` en una carpeta temporal limpia. Los tests ocultos y la referencia quedan fuera de esa carpeta; los tests se copian recién al evaluar. La referencia comprueba que el enunciado es resoluble y no se presenta al agente.

| ID | Tipo | Módulo permitido | Requisitos que se evalúan |
|---|---|---|---|
| 01-lotes | acotada | `lotes.py` | Dividir un iterable en listas de tamaño positivo, conservar orden, último lote incompleto y soporte de generadores; rechazar tamaño no entero, booleano o no positivo. |
| 02-intervalos | acotada | `intervalos.py` | Unir intervalos cerrados desordenados y los que se tocan, validar extremos, conservar la entrada y devolver listas ordenadas. |
| 03-importes | acotada | `importes.py` | Leer importes decimales con coma, signo opcional y hasta dos decimales, convertir exactamente a centavos; rechazar blancos internos, punto, exponentes y valores mal formados. |
| 04-espera | acotada | `espera.py` | Calcular espera exponencial con tope y jitter determinista recibido como fracción; validar intento, base, tope y fracción; evitar desbordes en intentos enormes. |
| 05-consulta | acotada | `consulta.py` | Actualizar parámetros de una URL: preservar repetidos ajenos, reemplazar todas las ocurrencias de las claves dadas, borrar con `None`, codificar caracteres y preservar fragmento. |
| 06-inventario | diseño | `inventario.py` | Libro de movimientos idempotentes por identificador, transferencias atómicas, sin saldo negativo, consultas y reversión única de movimientos; excepciones sin cambios parciales. |
| 07-planificador | diseño | `planificador.py` | Grafo de dependencias, validación de referencias y ciclos, tandas deterministas limitadas por capacidad, propagación de fallos y estado terminal; completar sólo tareas en curso. |
| 08-cache | diseño | `cache.py` | Caché LRU con TTL y reloj inyectado, capacidad positiva, expiración exacta, actualización de recencia, estadísticas de hits/misses y carga perezosa sin guardar fallos. |

Los cinco cambios acotados se resuelven con aproximadamente diez líneas añadidas o modificadas en un módulo chico. Los tres módulos de diseño apuntan a unas 80–150 líneas de solución, con varios requisitos que interactúan. Esa longitud es orientativa, no una métrica de corrección ni un límite impuesto al agente.

Antes del piloto, cada suite oculta debe fallar con el inicio y pasar con la referencia. Se guardan los conteos, el código y hashes SHA-256 del banco completo. Si un fallo de validación obliga a corregir el banco, la corrección ocurre **antes de cualquier respuesta del modelo** y se registra; después del piloto el banco no cambia.

## Protocolo

- Entorno previsto: Python 3.12.3, biblioteca estándar; `codex-cli 0.166.0`. El arnés comprueba ambas versiones antes de correr. Modelo exacto: `gpt-6.1-sol`, sin sustituciones.
- Cada llamada usa `codex exec --json -m gpt-6.1-sol -c model_reasoning_effort=NIVEL`, stdin cerrado, mismo prompt y configuración salvo el nivel. La configuración efectiva y el comando reproducible se documentan con el arnés.
- Se evita el contexto del repositorio anfitrión, sus instrucciones, memoria, integraciones y archivos privados mediante un entorno temporal controlado. Los controles de aislamiento realmente disponibles se declaran antes del piloto; no se afirma aislamiento del sistema de archivos si el mecanismo no lo impide.
- Una corrida parte de una copia nueva del inicio y de su enunciado. No se reutilizan conversaciones ni archivos entre corridas. No se le permite delegar ni acceder a Internet; se le pide editar sólo el módulo permitido. La evaluación utiliza una copia separada del resultado para que sus tests no alteren la medida del diff.
- Piloto: tarea `01-lotes`, una corrida por nivel, en orden aleatorio con semilla 20261113; las tres quedan registradas aparte y **no entran** al análisis. Sirve para detectar fallas del arnés, no para modificar la dificultad. Si el CLI falla por infraestructura, se registra y no se sustituye modelo o proveedor.
- Matriz principal: 8 tareas × 3 niveles × 3 repeticiones = **72 corridas**. Se mezcla la lista completa con `random.Random(20261113).shuffle`; se conserva el orden en un CSV antes de lanzarlas. Como máximo hay dos corridas simultáneas. El orden de inicio y la concurrencia real quedan registrados.
- Tiempo máximo por corrida: 600 segundos de reloj para el proceso del agente completo, desde su lanzamiento hasta su salida. Un timeout se termina junto con sus procesos descendientes, cuenta como no resuelto y conserva métricas parciales disponibles.
- Cada suite oculta tiene un timeout independiente de 30 segundos. Ningún resultado puede aprobar si el proceso falla, se agota el tiempo, faltan los tests o la suite no completa correctamente.
- Sin reintentos de respuestas para mejorar un resultado. Un error del CLI es una corrida no resuelta y se informa aparte. Si aparece una falla general de infraestructura, se pausa la matriz y se informa cobertura; no se completan filas inventadas. Un reinicio del arnés continúa sólo corridas nunca iniciadas, sin reemplazar observaciones.

## Métricas y criterios fijados

**Resuelta** significa: proceso del agente finalizado correctamente antes de 600 s y todos los tests ocultos pasan antes de 30 s. La salida textual del agente no decide ese resultado. Las suites verifican requisitos funcionales y casos límite del enunciado; no califican estilo.

Por corrida se conserva un CSV con ID, tarea, tipo, repetición, nivel, orden, estado del proceso, timeout, tests aprobados/total, resolución, tokens de entrada/salida/razonamiento cuando existan, tokens totales, tiempo de reloj, líneas agregadas y borradas, lista de archivos fuera de la lista blanca y detalles de error públicos. Los resultados del piloto van en otro CSV. Se guardan artefactos públicos del código generado y recibos de uso, sin transcripciones privadas ni rutas absolutas.

- **Tokens:** se usa el evento final de uso del propio CLI. Entrada + salida constituyen el total comparable; entrada en caché se informa aparte y no se suma de nuevo. Razonamiento sólo se informa separado si el CLI lo entrega y no se duplica al total. Si no existe el evento, el valor queda vacío: no vale cero. Se declara si no se puede separar razonamiento.
- **Tiempo:** segundos monotónicos de pared; incluye herramientas y esperas del agente, excluye la evaluación oculta. No equivale sólo al tiempo de inferencia ni es una medida aislada del servidor.
- **Líneas:** suma de líneas añadidas y borradas en archivos de texto respecto al inicio, incluyendo archivos nuevos y eliminados; un reemplazo cuenta una añadida y una borrada. Se excluyen sólo metadatos de Git y cachés de Python creadas por evaluación, que ocurre en otra copia. Los binarios se listan por separado y no reciben un conteo de líneas inventado.
- **Fuera de alcance:** cualquier archivo creado, eliminado o modificado fuera del módulo permitido por tarea. Incluso tests o documentación agregados cuentan. El enunciado y cualquier archivo auxiliar forman parte de la comparación. La métrica detecta diferencias finales; no detecta un archivo tocado y restaurado durante la corrida. No es una medida general de limpieza, seguridad o calidad.

El resumen presenta una tabla por nivel y tipo (15 corridas acotadas y 9 de diseño por nivel): porcentaje resuelto, mediana de tokens disponibles (con su denominador), mediana de segundos, porcentaje con cambios fuera de alcance y mediana de líneas tocadas. Las medianas principales incluyen corridas resueltas y fallidas cuando la métrica existe; se muestra además el corte de resueltas para hacer visible la influencia de fallos. Se entregan también resultados por tarea y todas las filas crudas.

No se hacen pruebas de significancia ni se seleccionan métricas después. Se describen diferencias numéricas, su consistencia entre tareas y sus límites. No se define ganador por una diferencia mínima de medianas. Con tres repeticiones, un caso aislado puede mover mucho el resultado.

## Reproducir

El banco, `medir.py` y las instrucciones operativas se agregan después de este commit de pre-registro, antes de correr modelos. No se requieren dependencias Python externas. El CLI debe estar instalado oficialmente, con acceso autorizado al modelo y a sus niveles. No se guardan credenciales ni configuración de cuentas en este repositorio.

## Lo que este experimento no demuestra

- No representa otros modelos, versiones del CLI, lenguajes, repositorios grandes, equipos o tareas de producción.
- Las tareas son chicas, artificiales y escritas por nosotros. Tres repeticiones por celda no estiman con precisión probabilidades generales.
- El modelo puede cambiar del lado del proveedor aunque el identificador se mantenga. No hay una semilla de muestreo del modelo controlada por este CLI; la semilla fija sólo el orden.
- Un solo CLI y modelo, Python y la carga variable del servidor limitan la generalización. Dos procesos simultáneos pueden competir por recursos; el orden mezclado reduce sesgos temporales, no los elimina.
- Los tests son evidencia funcional parcial; pasar no prueba ausencia de errores. Menos líneas o archivos extra no significa automáticamente código más limpio.
- Tokens no equivalen a costo monetario sin tarifas y tratamiento de caché. No se infieren importes ni descuentos de suscripción.
- Comparar `high` con `medium` no prueba una afirmación sobre el razonamiento máximo. El “90 % del código” del reel no es una variable definida por este protocolo.

El resumen final debe cerrar con **«Qué se puede decir en un reel»**: dos o tres frases apoyadas por los datos y afirmaciones que los datos no sostienen, aunque contradigan al reel original.
