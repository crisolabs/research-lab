"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading
from collections import namedtuple

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"

# Todo movimiento es un flujo de ``cantidad`` unidades desde ``origen`` hacia
# ``destino``; ``None`` representa el exterior del inventario.
_Movimiento = namedtuple("_Movimiento", "id tipo origen destino cantidad original")

# Un único cerrojo para todos los libros: las operaciones son breves y así las
# instancias sólo contienen datos simples.
_CERROJO = threading.RLock()


def _texto(valor, nombre):
    """Valida un string no vacío y lo devuelve como ``str`` exacto."""
    # Se mira type() y se normaliza con str.__str__ para que una subclase (o un
    # __class__ falsificado) no pueda colar igualdad o hash propios en el libro.
    if not issubclass(type(valor), str):
        raise ValueError(f"{nombre} debe ser un string no vacío")
    texto = str.__str__(valor)
    if not texto:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return texto


def _cantidad(valor):
    """Valida un entero positivo no booleano y lo devuelve como ``int`` exacto."""
    tipo = type(valor)
    if issubclass(tipo, bool) or not issubclass(tipo, int):
        raise ValueError("la cantidad debe ser un entero positivo no booleano")
    cantidad = int.__index__(valor)
    if cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return cantidad


class Inventario:
    """Saldos por ubicación con un historial de movimientos idempotentes."""

    def __init__(self):
        self._saldos = {}  # ubicación -> unidades
        self._movimientos = []  # en orden de aplicación
        self._por_id = {}  # identificador -> movimiento
        self._revertidos = set()  # identificadores de movimientos ya revertidos

    def saldo(self, ubicacion):
        """Devuelve las unidades disponibles en ``ubicacion``."""
        ubicacion = _texto(ubicacion, "la ubicación")
        with _CERROJO:
            return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        """Suma ``cantidad`` unidades a ``ubicacion``."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        self._registrar(_Movimiento(id, _INGRESO, None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        """Resta ``cantidad`` unidades de ``ubicacion`` si el saldo alcanza."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        self._registrar(_Movimiento(id, _RETIRO, ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        """Mueve ``cantidad`` unidades de ``origen`` a ``destino``, todo o nada."""
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        self._registrar(
            _Movimiento(id, _TRANSFERENCIA, origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        """Deshace, una única vez, el movimiento ``original``."""
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador del movimiento original")
        with _CERROJO:
            previo = self._por_id.get(id)
            if previo is not None:
                # La repetición se resuelve antes de mirar el original, que a
                # esta altura ya figura como revertido.
                if previo.tipo == _REVERSION and previo.original == original:
                    return
                raise ValueError(
                    f"el identificador {id!r} ya se usó con otra operación o argumentos"
                )
            objetivo = self._por_id.get(original)
            if objetivo is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if objetivo.tipo == _REVERSION:
                raise ValueError(f"{original!r} es una reversión y no se puede revertir")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            self._asentar(
                _Movimiento(
                    id,
                    _REVERSION,
                    objetivo.destino,
                    objetivo.origen,
                    objetivo.cantidad,
                    original,
                )
            )

    def historial(self):
        """Devuelve una copia independiente de los movimientos aplicados."""
        with _CERROJO:
            return [dict(zip(_Movimiento._fields, mov)) for mov in self._movimientos]

    def _registrar(self, mov):
        """Asienta ``mov`` salvo que sea la repetición exacta de uno previo."""
        with _CERROJO:
            previo = self._por_id.get(mov.id)
            if previo is None:
                self._asentar(mov)
            elif previo != mov:
                raise ValueError(
                    f"el identificador {mov.id!r} ya se usó con otra operación o argumentos"
                )

    def _asentar(self, mov):
        """Aplica y anota ``mov``; exige el cerrojo y un identificador libre."""
        cambios = {}
        if mov.origen is not None:
            disponible = self._saldos.get(mov.origen, 0)
            if disponible < mov.cantidad:
                raise ValueError(
                    f"saldo insuficiente en {mov.origen!r}: "
                    f"hay {disponible} y se necesitan {mov.cantidad}"
                )
            cambios[mov.origen] = disponible - mov.cantidad
        if mov.destino is not None:
            cambios[mov.destino] = self._saldos.get(mov.destino, 0) + mov.cantidad
        # Las validaciones terminaron: recién ahora se toca el estado.
        self._saldos.update(cambios)
        self._movimientos.append(mov)
        self._por_id[mov.id] = mov
        if mov.original is not None:
            self._revertidos.add(mov.original)
