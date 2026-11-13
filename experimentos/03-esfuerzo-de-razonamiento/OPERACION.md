# Cómo correr y auditar

Este banco usa únicamente Python 3.12.3 y `codex-cli 0.166.0` oficial (instalación npm). Requiere Node.js, bubblewrap (`bwrap`) y autenticación vigente del CLI. No instala dependencias ni copia credenciales. El agente medido usa un prompt fijo, sin instrucciones del repositorio anfitrión ni configuración de usuario, integraciones o memoria.

```bash
python3 medir.py validar
# Congelar este estado en un commit antes del piloto.
python3 medir.py piloto
python3 medir.py principal
python3 medir.py resumir
```

`validar` guarda los resultados de la comprobación inicio/referencia y un manifiesto SHA-256 de tareas, banco y arnés. No se vuelve a ejecutar después del primer modelo para cambiar contratos. El arnés rechaza cambios posteriores. Piloto y matriz se mezclan por separado con semilla 20261113. `orden-principal.json` preserva la cola antes de ejecutar. Se lanzan tandas de hasta dos procesos; cada tanda termina antes de lanzar la próxima. Las corridas se identifican establemente y no se repiten al retomar. Una corrida iniciada sin cierre requiere auditoría manual.

## Aislamiento y autenticación

Bubblewrap arma un sistema de archivos mínimo: runtime oficial de Codex, bibliotecas, herramientas del sistema, certificados, resolución DNS y carpeta de trabajo. El repositorio, la referencia, los tests ocultos y los directorios personales del host no se montan. HOME se crea vacío en el entorno efímero. El CLI usa `--ignore-user-config`, `--ignore-rules`, `--ephemeral`, `project_doc_max_bytes=0`, instrucciones de skills desactivadas, apps y multi-agente desactivados. El modelo recibe el mismo prompt para cada nivel.

El transporte oficial del CLI necesita red. Sus herramientas usan el sandbox `workspace-write`, con acceso de red desactivado. Si el sandbox no funciona, el piloto falla; no se usa un modo sin restricciones como alternativa silenciosa. La autenticación oficial existente se monta en sólo lectura para el CLI, sin copiarla a archivos persistentes. Ese montaje también está dentro del contenedor: **no se afirma resistencia ante un agente malicioso que intente leerlo**. El prompt prohíbe leer configuración o autenticación. No se guardan transcripciones completas: se extraen tipos de evento, uso numérico y tamaño del stderr en memoria. Los archivos persistentes del experimento no incluyen configuración, identidad de cuentas ni credenciales.

Los tests ocultos se ejecutan recién después de medir, en una copia separada dentro de otro bubblewrap, sin red, autenticación ni archivos personales. Se rechazan enlaces simbólicos y archivos especiales del candidato; se copian los archivos regulares del resultado y después los tests ocultos. Python usa `-I`; el runner importa unittest antes de agregar el módulo candidato a la ruta de importación. El diff se calcula antes de esa evaluación. Las suites usan unittest; `tests_total` cuenta métodos (y un error de importación cuenta como un test fallido). Los casos dentro de `subTest` amplían cobertura pero no aumentan ese denominador. La resolución requiere aprobar toda la suite, no un porcentaje de métodos.

## Registro de preparación anterior a las corridas

El commit `e22569c` contiene sólo el README de pre-registro. Se escribieron ocho enunciados, inicios, referencias y suites antes de pedir respuestas al modelo. La revisión independiente encontró que la referencia de intervalos devolvía `TypeError` ante un intervalo no iterable, aunque el enunciado exige `ValueError`: se corrigió la referencia y se agregaron casos para `None` y un entero **antes del piloto**. Esto aplica el contrato ya registrado; no usa resultados del modelo. La revisión del arnés también agregó los enlaces del sistema para `/bin` y `/sbin` en el entorno mínimo y reforzó la evaluación: rechaza enlaces y archivos especiales, copia todos los archivos regulares seguros del resultado y ejecuta los tests en aislamiento sin autenticación. También se corrigió el control de finitud de extremos enteros enormes en intervalos y se precisó, antes de correr, que base y tope de espera deben ser representables como float finito, con un test de rechazo para enteros demasiado grandes. Todo ocurrió antes del primer piloto.

Las referencias de diseño tienen 85, 73 y 68 líneas físicas antes de cualquier corrida. Dos quedan algo por debajo de la orientación de 80–150: se conserva el contrato claro y no se agregan líneas de relleno. Las soluciones del agente no se puntúan por aproximarse a esas longitudes. Las limitaciones y esa desviación deben acompañar la interpretación.

## Artefactos

- `banco-congelado.json`: hashes del banco y del arnés.
- `resultados/validacion_banco.json`: evidencia de ocho inicios que fallan y ocho referencias que pasan.
- `resultados/entorno.json`: versiones, prompt, controles de aislamiento y límites.
- `resultados/piloto.csv`: tres corridas excluidas de la tabla principal.
- `resultados/crudo.csv`: una fila por corrida principal efectivamente terminada; no se rellenan pendientes.
- `resultados/iniciadas/`, `corridas/`, `recibos/`: cola durable, métricas por corrida y uso informado por el CLI.
- `resultados/codigo/`: módulos generados, sin transcripciones.
- `resultados/resumen.md`: tablas reproducibles; interpretación y texto de reel revisados al finalizar.

## Fuentes del CLI

La documentación oficial describe el modo no interactivo, los eventos JSON y la configuración: [modo no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode), [referencia de configuración](https://learn.chatgpt.com/docs/config-file/config-reference). Se conserva la versión exacta, porque los nombres de campos y opciones pueden cambiar.

## Desviaciones de tamaño conservadas al cerrar

Las referencias acotadas cambian 10, 16, 11, 14 y 3 líneas respecto del inicio, contando cada bloque reemplazado como el máximo entre líneas añadidas y borradas. Intervalos y espera superan la orientación de aproximadamente diez líneas; importes la supera en una línea. Las referencias de diseño tienen 85, 73 y 68 líneas físicas. El resumen incluye la tabla completa y mantiene los grupos fijados, sin reclasificar ni cambiar contratos después del piloto. No se presenta este banco como cinco cambios de diez líneas exactas.

## Recalcular tablas sin perder la interpretación

`python3 medir.py resumir` reproduce las tablas numéricas desde los recibos y reemplaza `resultados/resumen.md` con una plantilla de interpretación. La respuesta, las aclaraciones y el párrafo de reel del resumen final fueron revisados editorialmente. Para conservarlos, guardá una copia del resumen antes de recalcular o compará el archivo recalculado con la versión guardada en Git. El arnés congelado no se modificó para generar el texto final.

## Cierre verificado

La revisión independiente final volvió a evaluar los 72 módulos principales guardados: todos pasan. Comprobó seis tests del arnés, 34 hashes del banco sin cambios, 75 recibos de uso concordantes, medianas, piloto separado, concurrencia máxima de dos agentes y privacidad sin hallazgos. La corrida más larga duró 131,884 segundos. No quedan ejecuciones ni controles del protocolo pendientes. Se conserva el trabajo mediante commits locales, sin push ni publicación.

## Extensión 01: xhigh y max

El pre-registro independiente es `EXTENSION-01.md` (commit `b267ab7`). El suplemento `extension.py` importa el arnés original sin cambiar sus archivos, llamada, medición ni evaluación. Usa semilla 2026111301 y mantiene separados tanto el piloto como los controles high. Los 34 hashes del manifiesto original se comprueban antes de cada fase; la primera comprobación fija también el hash del suplemento y el CSV original. No se ejecuta `medir.py validar` para esta extensión.

```bash
python3 -m unittest discover -s . -p 'test_*.py'
python3 extension.py verificar
python3 extension.py piloto
python3 extension.py principal
python3 extension.py resumir
```

La matriz de 56 se guarda antes del lanzamiento en `resultados/orden-extension.json`. El piloto tiene su propia cola `orden-piloto-extension.json` y su propio `piloto-extension.csv`. `crudo-extension.csv` contiene las 48 observaciones xhigh/max y los ocho controles high, distinguibles por nivel e identificador; el CSV original no se modifica. `resultados/extension-01/` contiene entorno, evidencia de hashes, inicios, corridas, recibos y módulos nuevos. Cada fase reutiliza `run_one`, con el mismo timeout, aislamiento, eventos y campos del CSV congelado. Se detiene ante un error CLI; una observación iniciada sin cierre no se repite.

`extension.py resumir` calcula las tablas desde ambos CSV y guarda además `extension-01/tablas.md`; sólo agrega la sección de extensión al resumen, preservando el texto original. La interpretación revisada se guarda en `extension-01/lectura.md` para conservarla al recalcular. El control no se mezcla con las tres repeticiones originales de high y no se usa para corregir artificialmente tiempos de otros niveles.
