# Enmienda operativa 02-01 · reconexión recuperada

El suplemento detuvo el bloque de `gpt-6-luna` tras 40 observaciones principales, con 80 nunca iniciadas. El parser clasificó una reconexión transitoria como un fallo definitivo aunque el CLI terminó correctamente. La pausa ocurrió antes de iniciar otra tanda. No se repite ninguna observación ni se cambian el banco, las métricas o los criterios pre-registrados.

## Evidencia leída directamente

La observación `principal-06-inventario-high-1` tiene retorno 0, timeout 0 y 5/5 tests ocultos aprobados. Su recibo conserva **25 eventos**: el evento de índice 18 es `error`, los índices 19–23 son eventos de herramientas y el índice 24, último, es `turn.completed`. Los índices empiezan en cero. El mensaje fue:

> Reconnecting... 2/5 (stream disconnected before completion: IO error: Connection reset by peer (os error 104))

El uso final leído del recibo es entrada 184.613 y salida 3.461: total 188.074 según la fórmula pre-registrada. La caché informada es 170.368 y el razonamiento 1.231; ninguno se vuelve a sumar. El recibo no se modifica.

El criterio congelado original decide resolución por retorno correcto, plazo y tests; un aviso de reconexión recuperada no es un fallo final. El suplemento agregó por error una condición más estricta. Se corrige esa implementación: sólo avisos explícitos de reconexión de red anteriores a un `turn.completed` posterior se conservan como advertencias, y aún se exigen retorno correcto, uso válido, ausencia de timeout y todos los tests. Un límite de cuota siempre detiene el proveedor, incluso si después aparece `turn.completed`. Los rechazos de esfuerzo, errores de modelo, autenticación y permisos también conservan sus bloqueos.

## Cambio auditable y alcance

- SHA-256 anterior de `extension02.py`: `622034d86b8b4557906158ab2e2b5ab0445d1026824e604c56ac636dd13d81f3`.
- SHA-256 corregido: `2ce9a5e3315f465f09157ae392e370304e2d8c8d505ba99404178b5b625291a4`.
- `resultados/extension-02/verificacion-congelado.json` permanece intacto. El verificador permite únicamente esta transición de hash, registrada explícitamente en `cambios-suplemento.json` con el commit correctivo; cualquier otro cambio sigue deteniendo la ejecución.
- `reclasificacion-02-01.json` conserva la observación original completa, los hashes del recibo y CSV originales, y los campos derivados corregidos. La observación pasa de infraestructura/sin resolución a completa/resuelta, con el aviso en un campo separado. Segundos, tokens, tests, diferencias de archivos y resto de métricas permanecen iguales.
- Las primeras 40 observaciones quedan en **34 resueltas y 6 fallos funcionales**. La corrección no agrega una observación ni oculta un fallo funcional. Se retoma exclusivamente la cola preexistente de 80 corridas nunca iniciadas, en el mismo orden.

La regresión local reproduce la secuencia exacta de tipos, el aviso y el uso conservados. También comprueba que cuota o rechazo de esfuerzo seguidos de `turn.completed` no se descartan y que un retorno no nulo sigue siendo infraestructura. No se hizo inferencia para esta corrección.
