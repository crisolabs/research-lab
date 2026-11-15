"""Libro de inventario con movimientos idempotentes y reversibles.

Todo movimiento traslada una cantidad de unidades desde un ``origen`` hacia un
``destino``; ``None`` en uno de los extremos significa «fuera del inventario».
Así, un ingreso no tiene origen, un retiro no tiene destino y una reversión es
el movimiento original con los extremos intercambiados.
"""

from collections import namedtuple
from threading import RLock

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"

# Registro inmutable de un movimiento aplicado. Sus campos son, en orden, las
# claves de cada entrada de ``Inventario.historial()``.
_Movimiento = namedtuple("_Movimiento", "id tipo origen destino cantidad original")


def _texto(valor, nombre):
    """Valida que ``valor`` sea un string no vacío y lo devuelve como ``str``.

    Se mira el tipo real (no ``__class__``) y se conserva sólo el contenido, de
    modo que una subclase de ``str`` no pueda alterar las comparaciones ni
    ejecutar código propio mientras se aplica un movimiento.
    """
    if not issubclass(type(valor), str):
        raise ValueError("%s debe ser un string no vacío" % nombre)
    texto = str.__str__(valor)
    if not texto:
        raise ValueError("%s no puede ser un string vacío" % nombre)
    return texto


def _entero_positivo(valor):
    """Valida que ``valor`` sea un entero positivo y lo devuelve como ``int``."""
    tipo = type(valor)
    if tipo is bool or not issubclass(tipo, int):
        raise ValueError("la cantidad debe ser un entero positivo, no booleano")
    cantidad = int.__index__(valor)
    if cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return cantidad


class Inventario:
    """Saldos por ubicación junto con el historial de movimientos aplicados.

    Los argumentos se validan por completo antes de tocar el estado, por lo que
    toda operación se aplica entera o falla con ``ValueError`` sin dejar rastro.
    """

    def __init__(self):
        self._saldos = {}  # ubicación -> unidades (ausente equivale a cero)
        self._movimientos = {}  # id -> _Movimiento, en orden de aplicación
        self._revertidos = {}  # id del movimiento original -> id de su reversión
        self._candado = RLock()

    # ------------------------------------------------------------- consultas

    def saldo(self, ubicacion):
        """Devuelve las unidades disponibles en ``ubicacion``."""
        ubicacion = _texto(ubicacion, "la ubicación")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        """Devuelve los movimientos aplicados, en orden, como diccionarios nuevos."""
        with self._candado:
            movimientos = list(self._movimientos.values())
        return [dict(zip(_Movimiento._fields, m)) for m in movimientos]

    # ----------------------------------------------------------- movimientos

    def ingresar(self, id, ubicacion, cantidad):
        """Suma ``cantidad`` unidades a ``ubicacion``."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _entero_positivo(cantidad)
        self._registrar(_Movimiento(id, _INGRESO, None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        """Resta ``cantidad`` unidades de ``ubicacion``, si alcanzan."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _entero_positivo(cantidad)
        self._registrar(_Movimiento(id, _RETIRO, ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        """Pasa ``cantidad`` unidades de ``origen`` a ``destino``, si alcanzan."""
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _entero_positivo(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        self._registrar(
            _Movimiento(id, _TRANSFERENCIA, origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        """Deshace, una única vez, el ingreso, retiro o transferencia ``original``."""
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador del movimiento original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo.tipo == _REVERSION and previo.original == original:
                    return  # repetición de una reversión ya aplicada
                raise ValueError(
                    "el identificador %r ya fue usado por otro movimiento" % id
                )
            objetivo = self._movimientos.get(original)
            if objetivo is None:
                raise ValueError("no existe el movimiento %r" % original)
            if objetivo.tipo == _REVERSION:
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError("el movimiento %r ya fue revertido" % original)
            self._aplicar(
                _Movimiento(
                    id,
                    _REVERSION,
                    objetivo.destino,
                    objetivo.origen,
                    objetivo.cantidad,
                    original,
                )
            )

    # --------------------------------------------------------------- interno

    def _registrar(self, movimiento):
        """Aplica un movimiento nuevo o reconoce la repetición de uno ya aplicado."""
        with self._candado:
            previo = self._movimientos.get(movimiento.id)
            if previo is None:
                self._aplicar(movimiento)
            elif previo != movimiento:
                raise ValueError(
                    "el identificador %r ya fue usado con otra operación o con"
                    " otros argumentos" % movimiento.id
                )

    def _aplicar(self, movimiento):
        """Asienta un movimiento con identificador nuevo si el origen tiene saldo.

        Los saldos resultantes se calculan aparte y recién se vuelcan al libro
        cuando ya no queda nada por comprobar.
        """
        origen = movimiento.origen
        destino = movimiento.destino
        cantidad = movimiento.cantidad
        nuevos = {}
        if origen is not None:
            restante = self._saldos.get(origen, 0) - cantidad
            if restante < 0:
                raise ValueError("saldo insuficiente en %r" % origen)
            nuevos[origen] = restante
        if destino is not None:
            nuevos[destino] = self._saldos.get(destino, 0) + cantidad

        self._saldos.update(nuevos)
        self._movimientos[movimiento.id] = movimiento
        if movimiento.original is not None:
            self._revertidos[movimiento.original] = movimiento.id

    # ------------------------------------------------- copia y serialización

    # El candado no se puede copiar ni serializar: el estado viaja sin él (y en
    # contenedores propios) y cada instancia reconstruida estrena su candado.

    def __getstate__(self):
        with self._candado:
            return {
                "saldos": dict(self._saldos),
                "movimientos": dict(self._movimientos),
                "revertidos": dict(self._revertidos),
            }

    def __setstate__(self, estado):
        self._saldos = dict(estado["saldos"])
        self._movimientos = dict(estado["movimientos"])
        self._revertidos = dict(estado["revertidos"])
        self._candado = RLock()
