# Extensión 02 · matriz de modelos y esfuerzos

Este documento amplía el Experimento 03 y se guarda **solo en un commit antes de cualquier sondeo, piloto o corrida nueva**. El banco, los criterios y las métricas no se ajustan después de observar respuestas. No se hace push ni publicación.

## Pregunta e hipótesis

¿Se repite en otros modelos que aumentar el esfuerzo no suma aciertos en este banco y sí aumenta el tiempo y los tokens? Se comparan niveles dentro de cada modelo. La hipótesis exploratoria permite empates, mejoras y retrocesos: ningún resultado se descarta por contradecir el reel. Los fallos por tarea pueden revelar diferencias que el techo de aciertos de las tandas anteriores ocultaba.

## Banco y contrato congelados

Se conservan las ocho tareas, los enunciados, los inicios, las referencias, los tests ocultos, el prompt y las métricas de [README.md](README.md). La verificación previa a este documento encontró coincidencia en los **34 archivos** de `banco-congelado.json`. El manifiesto no se vuelve a generar.

| Archivo | SHA-256 verificado |
|---|---|
| `banco-congelado.json` | `c16d9da850b15626aa31bb7cf9a8da10146c955fb4d3c9981c518b65b57949e9` |
| `banco.json` | `ada202ac451418354ec5f20bf157f9e8ed5b30c06f139c6f2a7e08e1e1562b45` |
| `medir.py` | `c010d324f171de63fee9fb3f2de559db8e1c6c3dd0a69749c7486132631acd03` |

El suplemento importa el arnés original para copiar tareas, evaluar y medir diferencias; no modifica `medir.py` ni el banco. Antes de cada bloque vuelve a comprobar todos los hashes y conserva el resultado. Se fijan Python **3.12.3**, Codex CLI **0.166.0** y Claude Code **2.1.317**, comprobados mediante sus comandos oficiales de versión antes de este pre-registro. El suplemento se guarda en Git antes del primer sondeo.

Cada corrida recibe una copia temporal nueva de `inicio/` y `TAREA.md`; nunca recibe los tests ocultos ni la referencia. La evaluación ocurre después, en otra copia. Se mantienen **600 segundos** de reloj para el agente y 30 para los tests; al vencer el plazo se termina el grupo de procesos. Resolver requiere salida correcta del agente dentro del plazo y todos los tests aprobados. El timeout cuenta como no resuelta; una interrupción por cuota se registra por separado y no cuenta como fallo funcional.

## Modelos, sondeos y orden

Se ejecuta un bloque por modelo, en este orden, sin sustituciones ni cambios de cuenta:

1. `gpt-6-luna`, mediante Codex CLI.
2. `claude-haiku-5-5`, mediante Claude Code CLI.
3. `claude-opus-5-5`, mediante Claude Code CLI.
4. `fable`, mediante Claude Code CLI; el identificador efectivo se confirma con el JSON del CLI, sin adivinarlo a partir del alias.

Antes del piloto de cada modelo se hacen llamadas triviales, excluidas de la matriz: «Respondé solamente OK. No uses herramientas». Se prueban en orden `low`, `medium`, `high`, `xhigh`, `max`; **no se usa ultra**. Cada sondeo tiene stdin cerrado y un plazo máximo de 600 segundos. Se conserva la respuesta técnica textual de rechazo, saneada si contiene información privada, y el uso disponible. Aceptación significa que la llamada completa sin rechazo del modelo o del nivel; que el parser acepte un argumento no basta. Si el CLI informa que ignoró el nivel, ese nivel no se presenta como esfuerzo efectivo.

Sólo entran niveles aceptados. Si ninguno es aceptado por falta de soporte de esfuerzo, se hace un sondeo sin `--effort` o sin la opción equivalente de Codex; si funciona, el modelo corre como **sin nivel**, ocho tareas por tres repeticiones. Si el modelo no está disponible, falla la autenticación o no hay un identificador efectivo verificable para el alias, se informa el bloqueo y no se atribuyen corridas a otro modelo. Se separan errores de configuración de fallos funcionales.

El piloto es una corrida de `01-lotes` con el menor nivel aceptado según el orden anterior, o sin nivel cuando corresponda. Cada modelo tiene un único piloto, excluido de todas las tablas principales. El piloto comprueba copia, herramientas, cierre, evaluación y recibo de uso; no habilita cambiar dificultad ni métricas. Un piloto con fallo funcional pero infraestructura y uso válidos se informa y permite medir la matriz; un fallo de infraestructura o ausencia de recibo impide iniciar el bloque principal.

La matriz tiene **8 tareas × niveles aceptados × 3 repeticiones**: 24 observaciones por nivel, hasta 120 por modelo y 480 nuevas en total si los cuatro aceptan los cinco niveles. No se fusionan con las 72 corridas originales ni con las 56 de la extensión 01. Para cada bloque se construye la lista en orden de tarea del banco, nivel aceptado según la lista anterior y repetición 1–3, y se mezcla con `random.Random(2026111302).shuffle`. La semilla sólo fija el orden, no la generación del modelo. El orden se guarda antes de la primera corrida principal del bloque.

Se permiten **como máximo dos procesos de agente en total**, también durante sondeos y pilotos; éstos se ejecutan de a uno. Dentro de la matriz se lanzan tandas de hasta dos y se espera su cierre antes de la siguiente. Se registran orden real y concurrencia. No se corren instalaciones, compilaciones ni otros trabajos pesados en paralelo; si fueran necesarios se usa `pesado`.

## Adaptador de Claude y aislamiento

Se usa el CLI oficial con la sesión de suscripción ya iniciada y stdin cerrado; no se extraen ni convierten tokens de autenticación. El comando base previsto, comprobado contra `claude --help`, es:

```sh
claude -p "$PROMPT" --model "$MODELO" --effort "$NIVEL" \
  --output-format json --restricted --setting-sources '' \
  --settings '{"disableAllHooks":true,"autoMemoryEnabled":false}' \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands --no-session-persistence --no-chrome \
  --permission-mode dontAsk --tools Read,Edit,Write,Bash \
  --allowedTools Read Edit Write 'Bash(python3:*)' < /dev/null
```

Para sondeos se deshabilitan todas las herramientas mediante `--tools ''`; para «sin nivel» se omite `--effort`. No se usa `--bare`: la ayuda declara que ese modo no lee OAuth y requiere API key o helper, lo que cambiaría el acceso solicitado. No se usa bypass de permisos, fallback de modelo ni continuación de sesiones.

El adaptador agrega aislamiento externo con una carpeta de usuario vacía y sólo los archivos de autenticación que el CLI oficial necesite, montados sin copiarlos ni publicarlos, además del runtime, las bibliotecas y los certificados. El agente trabaja únicamente en su copia temporal. No se montan carpetas personales de instrucciones, memorias, hooks, plugins, skills ni servidores MCP. Las herramientas disponibles se limitan a lectura y edición en la tarea y ejecución de Python; no se habilitan herramientas de navegación ni delegación. El acceso de red necesario para el proveedor no equivale a un aislamiento absoluto de red del proceso.

`--restricted` ignora configuraciones de usuario/proyecto/local y confina las herramientas de archivos; `--setting-sources ''` evita esas fuentes; los settings explícitos desactivan hooks y memoria automática; la configuración MCP vacía y estricta evita servidores personales; `--disable-slash-commands` desactiva skills y comandos. El suplemento conserva una lista exacta de flags, montajes públicos y controles efectivamente usados. Si una opción resulta incompatible con la autenticación o impide usar herramientas, se registra el error y se detiene antes de medir: no se reduce silenciosamente el aislamiento.

**Límites:** no se afirma que el modelo vea un sistema vacío. Permanecen el prompt de sistema y las herramientas incorporadas del proveedor; pueden existir políticas administradas del CLI. La autenticación oficial necesita ser legible por el proceso y no se afirma que un agente malicioso no pueda leerla. Los controles se verifican por el entorno y los flags, no por inspección completa del contexto interno del proveedor. Las corridas de **Codex cargan las instrucciones globales del usuario**, límite declarado para esta comparación aunque el arnés use `--ignore-user-config`, `--ignore-rules`, `project_doc_max_bytes=0` y opciones de skills desactivadas. Esos flags no prueban que toda instrucción global quede fuera del contexto efectivo. No se atribuye a Claude el mismo contexto que a Codex ni se interpreta una diferencia entre CLI como efecto puro del modelo.

## Métricas y definición previa de tokens

Se mantienen resolución, tests aprobados/total, segundos de reloj, líneas añadidas/borradas/tocadas, archivos y binarios fuera del módulo permitido, estado, retorno, timeout y error del protocolo original. Las medianas principales incluyen éxitos y fallos funcionales con datos disponibles, y se muestra además el corte de resueltas. Los valores ausentes quedan vacíos, nunca se convierten a cero. Se conservan recibos de uso separados de los CSV, sin transcripciones, credenciales, identidades de cuentas ni rutas privadas.

- **Codex:** se conserva el objeto crudo `usage` del último evento `turn.completed`: `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens` o cualquier campo de razonamiento entregado. **Total = input_tokens + output_tokens**. Caché y razonamiento no se suman otra vez. Si falta alguno de los dos campos del total, el total queda ausente.
- **Claude Code:** se conservan íntegros los objetos numéricos de `usage` y `modelUsage` cuando existan, además de duración informada, duración de API, número de turnos, subtipo y código de resultado. **Total = usage.input_tokens + usage.cache_creation_input_tokens + usage.cache_read_input_tokens + usage.output_tokens**. La entrada sin caché, la escritura y la lectura de caché son categorías distintas en ese recibo. Un campo de caché omitido se toma como cero sólo si existe un objeto de uso válido con entrada y salida; si faltan entrada o salida, el total queda ausente. Los desgloses de creación de caché y de thinking/razonamiento no se vuelven a sumar; tampoco se agrega `modelUsage` encima de `usage`. Los campos desconocidos se conservan y no se incorporan retroactivamente al total.

La comparación válida de tokens es **entre niveles de un mismo modelo y CLI**, bajo esta definición. Los totales de CLI diferentes pueden acumular llamadas, herramientas y caché de distinta manera; no son una medida homogénea de procesamiento ni de dinero. Aciertos y tiempos pueden compararse descriptivamente entre modelos con la advertencia de que también cambia el CLI, el aislamiento, el momento y la carga. No se infiere precio de suscripción a partir de tokens.

## Cuota y cierre incompleto

Si el proveedor devuelve un límite de uso o tasa, se conserva el mensaje técnico y se para el lanzamiento de nuevas corridas de ese proveedor. Una corrida afectada se marca **cuota**, sin incluirla en el denominador de resolución funcional ni en las medianas principales. Las corridas nunca iniciadas quedan pendientes; no se inventan observaciones ni se completan con ceros. Los intentos de sondeo y piloto tampoco se mezclan con la matriz.

Sólo se permite una espera por proveedor si su propio mensaje indica una ventana explícita de **hasta 15 minutos**. Se documenta esa ventana y se realiza una única comprobación trivial tras la espera, excluida de la matriz; la observación cortada no se reemplaza. Si persiste, no hay ventana explícita o supera 15 minutos, se cierra el bloque como incompleto y se indica cuántas corridas quedaron pendientes y cuántas fueron cortadas. No se cambian cuentas ni se reintenta en bucle. Después se continúa únicamente con el próximo modelo de **otro proveedor**, o se termina: un agotamiento de Anthropic no habilita seguir consumiendo con otro de sus modelos. Los modelos omitidos por ese motivo se identifican expresamente.

Otros errores generales de infraestructura también detienen el bloque y se informan aparte. Retomar sólo permite observaciones nunca iniciadas; una iniciada sin cierre requiere auditoría. Un rechazo de política no habilita reformular la tarea ni cambiar modelo para superarlo.

## Archivos y análisis previstos

Los CSV existentes permanecen intactos. Los datos nuevos se guardan en `resultados/crudo-gpt-6-luna.csv`, `crudo-claude-haiku-5-5.csv`, `crudo-claude-opus-5-5.csv` y `crudo-fable.csv`; el identificador efectivo de Fable se conserva dentro de las filas y recibos. Sondeos, pilotos, órdenes, inicios, resultados individuales, código permitido, recibos, versiones y verificaciones quedan separados bajo `resultados/extension-02/`. Un bloque inaccesible puede tener CSV sólo con cabecera y un estado explícito, sin filas ficticias. Cada bloque cerrado tiene un commit propio, incluso si queda incompleto.

Se agrega a `resultados/resumen.md` la sección **«Extensión 02: matriz por modelo»**, conservando las tandas anteriores. La tabla modelo × nivel informa cobertura, resueltas/observadas evaluables, mediana de segundos, mediana de tokens y su denominador, y fuera de alcance. Se muestran cuotas, errores de infraestructura, timeouts y pendientes aparte. La tabla por tarea permite ver cada fallo y el corte de resueltas evita ocultarlo en una mediana.

Por modelo se calcula la razón **nivel más alto / nivel más bajo aceptado** para medianas de segundos y tokens. El orden es `low < medium < high < xhigh < max`; «sin nivel» no tiene razón. Si falta cobertura comparable se informa el límite y no se presenta un cociente como confirmación; con un solo nivel no hay comparación. Se incluyen como referencia los cinco niveles anteriores de `gpt-6.1-sol`, sin fusionar sus controles contemporáneos con las tres repeticiones originales.

La lectura responde si el patrón de igual resolución y mayor tiempo se observa en todos los modelos **medidos**, si hay excepciones y qué tareas las producen. Se muestran los datos que contradicen la hipótesis. No se aplican pruebas de significancia ni se define un ganador por diferencias pequeñas. Se actualiza únicamente la fila del Experimento 03 en la tabla «Experimentos» del README raíz.

## Lo que este experimento no demuestra

El banco artificial de Python conserva su techo y sus tres repeticiones por celda; no representa producción ni todos los modelos. Niveles con el mismo nombre no garantizan igual cantidad de razonamiento entre proveedores. Aceptar el parámetro tampoco demuestra el procesamiento interno real. Modelos remotos y alias pueden cambiar aunque se fije la versión del CLI. Cada bloque ocurre en otro momento y el host está compartido; no se aísla un efecto causal del esfuerzo o del modelo. Los tests son parciales y no miden limpieza. Los tokens no son dinero ni se comparan sin advertencia entre CLI. Cuotas y modelos inaccesibles reducen cobertura; una matriz incompleta no sostiene una afirmación universal.

El resumen termina con **«Qué se puede decir en un reel»**: dos o tres frases que los datos sostengan y las que no sostengan. Ni el «90 % del código más limpio» ni una regla general del triple de tiempo se afirman sin una medida que las respalde.
