# Operación y evidencia de la extensión 02

El protocolo está en `EXTENSION-02.md`; las observaciones y su lectura están en `resultados/resumen.md`. La extensión usa Python 3.12.3, Codex CLI 0.166.0 y Claude Code 2.1.317, sin dependencias Python externas. Los modelos se invocaron por los CLI oficiales con las sesiones de suscripción existentes, sin cambiar cuentas ni extraer credenciales.

## Comandos

Desde la carpeta del experimento:

```sh
python3 extension02.py verificar
python3 extension02.py sondear gpt-6-luna
python3 extension02.py piloto gpt-6-luna
python3 extension02.py principal gpt-6-luna
python3 resumir02.py
```

Las mismas acciones por modelo se usaron en el orden `gpt-6-luna`, `claude-haiku-5-5`, `claude-opus-5-5`, `fable`, sólo cuando sus controles previos lo permitieron. No se ejecuta una matriz después de un piloto bloqueado ni se reintenta automáticamente una observación iniciada sin cierre. Los estados actuales conservan los cierres: repetir estos comandos no autoriza reabrirlos. El alias `fable` no llegó a piloto ni a matriz. `resumir02.py` es el generador final de la extensión: la acción antigua `extension02.py resumir` quedó como herramienta preliminar y no incluye todos los controles de presentación del informe final.

El suplemento tiene un candado entre procesos que cubre cada fase completa; `.ejecucion.lock` es un archivo de ejecución ignorado por Git. Las matrices usan tandas de hasta dos agentes y esperan el cierre de ambos antes de iniciar otra tanda. Sondeos y pilotos se ejecutan de a uno. Cada agente dispone de 600 segundos y cada evaluación oculta de 30; el arnés termina el grupo de procesos al vencer el plazo. No hubo instalaciones, compilaciones ni pruebas pesadas en esta extensión.

## Flags y montajes efectivos de Claude

La lista completa de argumentos públicos realmente usados queda en `resultados/extension-02/aislamiento.json`. El comando de tarea usa el mismo prompt de `medir.py` y esta configuración:

```sh
claude -p "$PROMPT" --model "$MODELO" --effort "$NIVEL" \
  --output-format json --restricted --setting-sources '' \
  --settings '{"disableAllHooks":true,"autoMemoryEnabled":false}' \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --disable-slash-commands --no-session-persistence --no-chrome \
  --permission-mode dontAsk --tools Read,Edit,Write,Bash \
  --allowedTools Read Edit Write 'Bash(python3:*)' < /dev/null
```

Los sondeos usan el prompt trivial pre-registrado y `--tools ''`, sin herramientas. No se usó `--bare`, porque su ayuda declara que no lee OAuth. Tampoco se usó bypass de permisos, fallback de modelo, continuación de conversación ni otros perfiles.

El aislamiento externo de `bubblewrap` crea un usuario vacío y monta únicamente el binario oficial nativo en `/opt/claude`, las credenciales oficiales en lectura, el runtime del sistema y los certificados en lectura, y la copia nueva de la tarea en `/work` con escritura. El montaje de autenticación se hace directamente, sin copiar su contenido al experimento. No se montan las carpetas personales de instrucciones, memorias, hooks, plugins, skills ni configuración MCP. El CLI sólo recibe `inicio/` y `TAREA.md`; los tests ocultos y la referencia se copian a un entorno separado después de la medición. Las variables de entorno se reconstruyen con rutas internas al aislamiento, idioma y semillas de Python; no se heredan variables personales ni credenciales de API.

`--restricted` y las fuentes vacías evitan configuración de usuario/proyecto/local; los settings explícitos desactivan hooks y memoria automática. MCP usa una configuración vacía y estricta; los comandos y skills están desactivados; las herramientas de archivos quedan confinadas al trabajo. Sólo se autoriza Bash para Python. Esto no demuestra que un proceso malicioso no pueda leer su autenticación oficial ni que toda conexión de red esté bloqueada: la red necesaria para el proveedor permanece disponible. También quedan las instrucciones incorporadas y posibles políticas administradas del CLI; no se inspeccionó el contexto interno completo del proveedor.

Haiku y una corrida principal de Opus recibieron una denegación Bash, pese a terminar con retorno 0 y pasar 3/3 tests. El recibo conserva cantidad y nombre de la herramienta, no entradas arbitrarias. El comando denegado es desconocido: no se demostró que Python permitido estuviera inaccesible ni que esos modelos no pudieran resolver. El control conservador del adaptador detuvo sus bloques y limita la cobertura; no se amplió el permiso ni se reformuló el pedido para superar la denegación.

## Codex y el límite de contexto

Se reutiliza íntegramente `medir.command` y se cambia únicamente el modelo solicitado; el sondeo reemplaza el prompt por el trivial. El CLI recibe `exec --json --ephemeral --ignore-user-config --ignore-rules --skip-git-repo-check --color never -s workspace-write`, el modelo, `model_reasoning_effort`, `project_doc_max_bytes=0`, skills e integraciones desactivadas y red desactivada en el sandbox de herramientas. El entorno externo sólo expone runtime, certificados, autenticación oficial en lectura y la copia temporal de la tarea. El prompt impide delegación e Internet.

Las corridas de Codex cargan instrucciones globales del usuario, límite declarado por el protocolo. Los flags anteriores no prueban ausencia de toda instrucción global en su contexto efectivo. Claude y Codex tampoco comparten necesariamente prompt de sistema, herramientas o contabilidad de uso, por lo que una diferencia entre sus resultados no aísla un efecto puro del modelo.

## Integridad, uso y generación del informe

`verificacion-congelado.json` conserva los 34 hashes y el hash inicial del suplemento. `ENMIENDA-02-01.md`, `cambios-suplemento.json` y `reclasificacion-02-01.json` documentan la única corrección de clasificación de una reconexión recuperada de Luna; se conservaron la observación original completa y el recibo intacto. No se cambió el banco, no se repitió esa observación y no se ajustaron sus tiempos, tokens ni tests. Un evento de cuota siempre bloquea al proveedor aunque exista un cierre posterior. Las observaciones nunca iniciadas conservaron la cola preexistente.

Los cuatro CSV anteriores a esta extensión se comparan por hash y permanecen idénticos. Los CSV nuevos usan el terminador CRLF estándar de `csv.DictWriter`, igual que los arneses anteriores; para comprobar espacios puede usarse `git -c core.whitespace=cr-at-eol diff --check`. Al retomar Luna, el exportador agregó al CSV de su piloto una columna vacía de advertencias; se restauró el CSV del commit de respaldo para conservarlo idéntico, sin cambiar un solo valor medido. Los recibos numéricos conservan los campos crudos: los desgloses de thinking de Claude pueden estar anidados aunque la columna normalizada de razonamiento esté vacía. Esa ausencia de columna no significa cero razonamiento y no cambia la fórmula del total.

`resumir02.py` está separado del código de medición fijado. Lee los CSV y estados, excluye los ocho controles high de la referencia Sol, calcula medianas y razones desde los valores crudos mediante aritmética decimal y escribe tablas y trazabilidad sin modificar CSV. Conserva la lectura editorial de `resultados/extension-02/lectura.md` y todo el resumen anterior al encabezado de extensión 02. `resumen-trazabilidad.json` registra su hash, el del código de medición intacto, los hashes de entrada, los conteos y los cocientes sin redondeo previo. El repositorio no incluye transcripciones, contenido de autenticación, identificadores de cuentas ni rutas privadas.

## Continuación bajo ENMIENDA-02-02

Las secciones anteriores describen el protocolo anterior. La continuación usa `extension0202.py`, un suplemento separado: no modifica `extension02.py`, `medir.py`, el banco ni las observaciones históricas. `resultados/extension-02/protocolo-02-02/historicos-congelados.json` conserva sus hashes y el verificador los exige antes de cada fase. Las versiones siguen siendo Python 3.12.3, Codex CLI 0.166.0 y Claude Code 2.1.317.

```sh
python3 -m unittest test_extension0202.py test_diagnosticar_luna02.py
python3 extension0202.py verificar
python3 extension0202.py sondear claude-haiku-5-5
python3 extension0202.py piloto claude-haiku-5-5
python3 extension0202.py principal claude-haiku-5-5
# Cerrar y commitear Haiku; después repetir las tres fases para Opus y Fable.
python3 extension0202.py sondear claude-opus-5-5
python3 extension0202.py piloto claude-opus-5-5
python3 extension0202.py principal claude-opus-5-5
python3 extension0202.py sondear fable
python3 extension0202.py piloto fable
python3 extension0202.py principal fable
python3 diagnosticar_luna02.py
python3 resumir0202.py
```

`fable` es sólo la clave interna del archivo y del runner: el argumento enviado al proveedor es siempre `--model claude-fable-5-2`. El efectivo se extrae del mayor `outputTokens` de `modelUsage`; se conserva el uso de todos los IDs y los auxiliares. Si difiere del pedido se declara, sin adjudicarlo al modelo solicitado. Un empate no identifica un principal.

La configuración de Claude cambia únicamente sus herramientas: `--tools Read,Edit,Write,Glob,Grep,Bash --allowedTools Read Edit Write Glob Grep Bash`. Bash no tiene restricción de comando y trabaja en `/work`. Se mantienen todos los flags y montajes anteriores, sin settings personales, MCP, comandos, memoria ni persistencia. `denegaciones` cuenta las herramientas denegadas sin anular observaciones; los tests ocultos evalúan el resultado. Los comandos arbitrarios del agente no se guardan en los recibos de la matriz.

Los CSV nuevos usan el sufijo `-02-02.csv` y los artefactos están bajo `protocolo-02-02/`; los CSV y recibos anteriores permanecen intactos y fuera de la nueva matriz de Claude. La semilla nueva de cada matriz es 2026111303. Se conservan dos agentes como máximo, 600 segundos por agente, tandas que esperan ambos cierres, el candado de fase y la parada por cuota de todo el proveedor. Los comandos de fases posteriores sólo corresponden cuando los estados y la cuota lo permitan; no autorizan saltar bloqueos.

El diagnóstico usa la semilla 2026111304 y se ejecuta de a una corrida, después de los bloques de Claude. `diagnosticar_luna02.py` conserva el mensaje final completo y los comandos de eventos `item.completed`, con estado y retorno, pero no las salidas arbitrarias de herramientas ni el transcript. El saneado excluye correos, rutas personales, URLs y patrones de credenciales; no trunca el mensaje final. Sus seis observaciones, CSV y nota quedan en `diagnostico-luna-low/`, excluidos del resumen numérico de la matriz. No se reclasifica ninguna observación original.

`resumir0202.py` lee los CSV históricos de Sol y Luna y los CSV nuevos de Claude. Genera tablas, razones sobre medianas crudas y trazabilidad bajo `protocolo-02-02/`, preservando la sección anterior a Extensión 02. Su lectura editorial está separada en la misma carpeta. No invoca modelos ni escribe datos crudos.

### Cierre real de la continuación

Haiku cerró 120 observaciones (119 resueltas) y Opus 120 (117 resueltas dentro del plazo; tres timeouts). Fable cerró incompleto por cuota tras 28 observaciones: 27 evaluables, 22 resueltas, cinco timeouts y 92 pendientes. Se pidió y se observó `claude-fable-5-2`; los timeouts sin JSON final conservan identidad y uso ausentes. No hubo llamadas posteriores a Anthropic ni cambios de cuenta.

El cierre explícito “You've reached your Fable limit.” no coincidía con las frases de cuota del parser y quedó inicialmente como infraestructura, que igualmente cortó el lanzamiento al cerrar la tanda. `python3 clasificar_cuota_fable02.py` aplica la regla de cuota ya registrada sin llamar modelos: conserva la observación, el CSV y el estado originales, verifica el recibo intacto y cambia sólo estado, cuota y error en el derivado. La evidencia está en `protocolo-02-02/fable/auditoria-cuota/`. El candidato medido no se modificó; la observación no se repitió ni cambió sus métricas o tests.

El diagnóstico de Luna cerró sus seis observaciones separadas: dos resueltas y cuatro con cero líneas cambiadas. Conserva los finales completos y los comandos con estado y retorno, sin salidas arbitrarias ni transcripciones completas. Los cuatro finales sin cambios reconocen el bloqueo ante comandos de lectura fallidos; no prueban la causa individual de los once fallos originales. No se reparó el entorno ni se hicieron corridas extra.

```sh
python3 resumir0202.py
python3 verificar_cierre0202.py
python3 -m unittest test_extension0202.py test_diagnosticar_luna02.py
```

El verificador no invoca proveedores: verifica el candidato medido, los 34 hashes del banco, 584 archivos históricos, CSV frente a observaciones/recibos, el corte por cuota y su auditoría, el orden y la concurrencia reconstruida, la separación de los seis diagnósticos, la nota de diez líneas, los denominadores del resumen y la única fila modificada del README raíz. Deja su evidencia en `protocolo-02-02/validacion-cierre.json`. Los tokens ausentes por timeout siguen ausentes; las razones sobre recibos disponibles muestran n y su límite de comparabilidad.
