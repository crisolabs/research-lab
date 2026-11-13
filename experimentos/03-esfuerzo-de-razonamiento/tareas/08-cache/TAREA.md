# Caché LRU con vencimiento
Creá `Cache(capacidad, ttl, reloj)` en `cache.py`. `capacidad` es entero positivo, no booleano; `ttl` es int/float finito positivo, no booleano; valores inválidos → `ValueError`. `reloj` es callable que devuelve un número no decreciente de segundos; no hace falta validarlo. Las claves son hashables y los valores pueden ser cualquiera, incluido `None`.

API:
- `poner(clave, valor)`: antes elimina todas las entradas vencidas; guarda o reemplaza el valor con vencimiento `ahora + ttl` y lo marca como el más reciente. Si falta espacio elimina la entrada viva menos recientemente usada. Devuelve `None`.
- `obtener(clave, defecto=None)`: purga vencidas, devuelve valor si existe y actualiza recencia sin renovar TTL; si no, devuelve defecto. Suma un hit o un miss respectivamente.
- `obtener_o_crear(clave, fabrica)`: purga vencidas; si existe, devuelve y actualiza recencia con un hit. Si no, suma un miss, llama `fabrica()` sin argumentos y guarda su resultado con un TTL que empieza cuando la fábrica termina. Si la fábrica lanza, propaga la excepción, no guarda valor y no elimina ninguna entrada viva. La fábrica no llama al caché recursivamente. El reloj puede avanzar mientras trabaja.
- `borrar(clave)`: purga vencidas y elimina la clave si existe; devuelve bool. No cambia hits/misses.
- `claves()`: purga vencidas y devuelve lista de claves vivas de menos a más reciente. La lista es una copia.
- `estadisticas()`: devuelve copia `{'hits': entero, 'misses': entero}`. No modifica recencia ni contadores.

Una entrada vence cuando `ahora >= vencimiento` (frontera inclusiva). Las actualizaciones con `poner` renuevan su TTL; las lecturas no. No uses tiempo real ni threads: usá sólo el reloj inyectado y la biblioteca estándar.

Editá únicamente `cache.py`. Usá sólo la biblioteca estándar de Python. No modifiques este enunciado ni agregues otros archivos. No accedas a Internet ni delegues.
