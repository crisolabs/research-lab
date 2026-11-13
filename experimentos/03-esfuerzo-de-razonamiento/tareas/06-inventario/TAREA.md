# Libro de inventario
Creá `Inventario()` en `inventario.py`, sin dependencias externas. Cada ubicación empieza con saldo cero. Las ubicaciones e identificadores de movimiento deben ser strings no vacíos; de lo contrario `ValueError`. Las cantidades deben ser enteros positivos y no booleanos.

API:
- `saldo(ubicacion)`: devuelve entero; valida ubicación.
- `ingresar(id, ubicacion, cantidad)`: suma unidades.
- `retirar(id, ubicacion, cantidad)`: resta unidades; si no alcanza, `ValueError`.
- `transferir(id, origen, destino, cantidad)`: resta del origen y suma al destino atómicamente; origen y destino deben ser distintos; saldo insuficiente → `ValueError` sin efectos.
- `revertir(id, original)`: revierte exactamente una vez un movimiento existente de ingresar/retirar/transferir, con un identificador nuevo. Deshace sus variaciones y valida que ningún saldo quede negativo. No se puede revertir una reversión, ni un movimiento ya revertido. Original inexistente o restricciones incumplidas → `ValueError` sin efectos.
- `historial()`: lista de diccionarios en orden de aplicación con claves `id`, `tipo`, `origen`, `destino`, `cantidad`, `original`. `tipo` es `ingreso`, `retiro`, `transferencia` o `reversion`. Ingreso usa origen `None`; retiro usa destino `None`; movimientos no reversión usan original `None`. La reversión copia cantidad y usa origen/destino intercambiados respecto del movimiento original. Devolvé una copia que se pueda modificar sin alterar el libro.

Idempotencia: repetir el mismo identificador con la misma operación y argumentos no cambia nada ni agrega historial (también una reversión repetida). Reusar un identificador con argumentos distintos lanza `ValueError`. Validá argumentos antes de aplicar. Toda excepción conserva saldos, historial, identificadores y marcas de reversión; un intento fallido no consume su identificador. Los métodos de mutación devuelven `None`.

Editá únicamente `inventario.py`. Usá sólo la biblioteca estándar de Python. No modifiques este enunciado ni agregues otros archivos. No accedas a Internet ni delegues.
