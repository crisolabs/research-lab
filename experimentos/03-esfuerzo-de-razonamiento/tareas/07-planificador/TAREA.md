# Planificador de dependencias
Creá `Planificador(dependencias, capacidad)` en `planificador.py`. `dependencias` es un diccionario de nombres string no vacíos a iterables de nombres de prerrequisitos. Copiá su contenido; las repeticiones de una dependencia se ignoran. Los prerrequisitos deben existir como claves. Rechazá nombres inválidos, referencias desconocidas y ciclos (incluso auto dependencia) con `ValueError`. `capacidad` es entero positivo, no booleano.

API:
- `estados()` devuelve una copia del diccionario nombre → estado. Los estados son `pendiente`, `en_curso`, `listo`, `fallo` o `bloqueado`; todos empiezan pendientes.
- `tomar()` devuelve la lista de nuevas tareas lanzadas. Seleccioná en orden lexicográfico entre pendientes cuyos prerrequisitos estén todos `listo`, hasta llenar los lugares libres de capacidad. Marcalas `en_curso`; llamadas repetidas no relanzan una tarea. Una tarea sin dependencias está habilitada. El orden de entrada del diccionario no debe afectar el resultado.
- `completar(nombre, exito=True)` sólo acepta tareas `en_curso`; nombre desconocido, estado incorrecto o `exito` que no sea bool → `ValueError`, sin cambiar nada. Con éxito marca `listo`; de lo contrario `fallo` y marca `bloqueado` toda tarea pendiente que dependa directa o transitivamente de un fallo o bloqueo. No bloquea tareas independientes. Devuelve `None`.
- `terminado()` devuelve bool: todas las tareas están `listo`, `fallo` o `bloqueado`. El grafo vacío está terminado.

No lances threads ni ejecutes callbacks: el módulo sólo administra estados. Las excepciones no cambian el planificador. Conservar la entrada y las copias que devuelve el objeto no deben permitir modificar su estado interno.

Editá únicamente `planificador.py`. Usá sólo la biblioteca estándar de Python. No modifiques este enunciado ni agregues otros archivos. No accedas a Internet ni delegues.
