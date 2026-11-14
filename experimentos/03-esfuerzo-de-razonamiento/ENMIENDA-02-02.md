# Enmienda 02-02 · completar Claude y observar los fallos de Luna

Este documento se guarda solo en un commit antes de los sondeos, pilotos y corridas de esta continuación. Cambia únicamente lo que sigue; el banco, el prompt, las métricas, los tests ocultos y los criterios funcionales de `EXTENSION-02.md` permanecen congelados. No se hace push.

## 1. Herramientas de Claude y denegaciones

Claude recibe `Read`, `Edit`, `Write`, `Glob`, `Grep` y `Bash`, con autorización de Bash sin restricción de comando, trabajando en la copia temporal de la tarea. Se conserva el aislamiento externo actual, las fuentes de settings vacías, hooks y memoria desactivados, MCP vacío y estricto, comandos y skills desactivados y ausencia de persistencia. No se agregan carpetas personales ni herramientas de navegación o delegación. La red del proveedor y la autenticación oficial conservan los límites declarados; no se afirma aislamiento absoluto.

Una denegación de herramienta no invalida la corrida ni detiene el bloque. La columna `denegaciones` registra su cantidad y el recibo conserva los nombres de las herramientas; la resolución se decide por retorno, plazo y tests ocultos, igual que en las otras corridas. Las dos observaciones principales de Opus y el piloto anterior de Haiku se conservan intactos como **protocolo anterior**, fuera de la nueva matriz; los demás sondeos y pilotos anteriores también permanecen separados. La continuación usa archivos nuevos, sin sobrescribir observaciones anteriores.

## 2. Identidad de Fable

Se solicita el ID explícito `claude-fable-5-2`, nunca el alias. El modelo efectivo es el identificador de `modelUsage` con más `outputTokens`; se conserva la lista completa de modelos y sus usos. Un empate máximo o la ausencia de salida atribuible impiden verificar una identidad principal y se informan como infraestructura. Si el CLI informa otro ID principal, el bloque continúa rotulado con ese ID, y se declara la diferencia frente al pedido. Los otros modelos con menos salida se anotan como auxiliares con sus cantidades, sin sumar su uso otra vez al total ni confundirlos con el principal.

## 3. Bloques, orden y cierre

Se corren bloques nuevos y completos en el orden **Haiku, Opus, Fable**, con los IDs solicitados `claude-haiku-5-5`, `claude-opus-5-5` y `claude-fable-5-2`. Se conservan los sondeos de esfuerzo, el único piloto de `01-lotes` por modelo excluido de la matriz, ocho tareas, tres repeticiones por tarea y nivel aceptado, hasta dos agentes simultáneos y 600 segundos por agente. Los sondeos y pilotos son seriales. El orden se fija antes de cada matriz con `random.Random(2026111303).shuffle`, sobre la misma lista base del protocolo; se guarda antes de iniciar la primera observación.

Se conserva sin cambios la regla de cuota de `EXTENSION-02.md`: no se cambia cuenta ni se insiste; una cuota de Anthropic cierra también los siguientes modelos de ese proveedor. Se cierran como incompletos los bloques afectados y se continúa sólo cuando el protocolo lo permita. Cada bloque cerrado tiene su propio commit, incluso si queda incompleto u omitido. Los artefactos de esta continuación se guardan bajo `resultados/extension-02/protocolo-02-02/` y los CSV principales se distinguen con el sufijo `-02-02.csv`. El suplemento nuevo verifica el banco, las versiones fijadas y los hashes de los archivos históricos antes de cada fase.

## 4. Diagnóstico separado de Luna low

Después de los bloques de Claude se hacen exactamente seis corridas de diagnóstico con `gpt-6-luna`, esfuerzo `low`: dos de `04-espera`, dos de `01-lotes` y dos de `08-cache`. El orden se mezcla con `random.Random(2026111304).shuffle` y se guarda antes de correr. Se mantienen prompt, copia nueva, límites de tiempo, herramientas y evaluación del protocolo. Se conserva el mensaje final del agente y la lista de comandos ejecutados, saneados para excluir datos privados, junto con los tests y las diferencias de archivos. No se entregan tests ocultos al agente.

Estos diagnósticos se guardan en `resultados/extension-02/diagnostico-luna-low/`, con CSV crudo y una nota de diez líneas. Se describe lo observado cuando no cambia archivos: si anuncia un cierre, pide confirmación, falla al aplicar un cambio o propone código en texto. Si no se reproduce el comportamiento se dice así. No se reclasifica ninguna corrida original ni se incorpora diagnóstico alguno a la matriz o sus medianas.

## 5. Resumen

La sección «Extensión 02» presenta los cinco modelos, con Sol y Luna históricos intactos y los bloques nuevos de Claude separados del protocolo anterior. Se muestran cobertura, resolución, tiempo, tokens, denegaciones y fallos por tarea; las razones máximo/bajo sólo se calculan con cobertura comparable según el protocolo. Se agregan el hallazgo del diagnóstico de Luna, los límites y «Qué se puede decir en un reel», con dos o tres frases que distingan lo sostenido de lo no sostenido. Se actualiza únicamente la fila del experimento en el README raíz.
