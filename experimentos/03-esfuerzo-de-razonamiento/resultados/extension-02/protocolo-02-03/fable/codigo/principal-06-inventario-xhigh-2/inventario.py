"""Libro de inventario con movimientos idempotentes y reversibles."""

import threading

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"

# Cada movimiento se guarda como una tupla inmutable con este orden de campos.
_CLAVES = ("id", "tipo", "origen", "destino", "cantidad", "original")


def _texto(valor, nombre):
    """Valida un string no vacío y lo devuelve como ``str`` exacto."""
    if not isinstance(valor, str):
        raise ValueError(f"{nombre} debe ser un string no vacío")
    valor = str.__str__(valor)  # neutraliza subclases de str
    if not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor):
    """Valida un entero positivo no booleano y lo devuelve como ``int`` exacto."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("cantidad debe ser un entero positivo")
    valor = int.__int__(valor)  # neutraliza subclases de int
    if valor <= 0:
        raise ValueError("cantidad debe ser un entero positivo")
    return valor


class Inventario:
    """Saldos por ubicación con un historial de movimientos."""

    def __init__(self):
        self._candado = threading.RLock()
        self._saldos = {}  # ubicación -> saldo
        self._movimientos = {}  # id -> movimiento
        self._historial = []  # movimientos en orden de aplicación
        self._revertidos = set()  # ids de movimientos ya revertidos

    # -- consultas ---------------------------------------------------------

    def saldo(self, ubicacion):
        ubicacion = _texto(ubicacion, "ubicacion")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._candado:
            return [dict(zip(_CLAVES, mov)) for mov in self._historial]

    # -- movimientos -------------------------------------------------------

    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "id")
        ubicacion = _texto(ubicacion, "ubicacion")
        cantidad = _cantidad(cantidad)
        with self._candado:
            self._registrar((id, _INGRESO, None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "id")
        ubicacion = _texto(ubicacion, "ubicacion")
        cantidad = _cantidad(cantidad)
        with self._candado:
            self._registrar((id, _RETIRO, ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "id")
        origen = _texto(origen, "origen")
        destino = _texto(destino, "destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        with self._candado:
            self._registrar((id, _TRANSFERENCIA, origen, destino, cantidad, None))

    def revertir(self, id, original):
        id = _texto(id, "id")
        original = _texto(original, "original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                # La repetición se resuelve antes de mirar el original, que
                # para entonces ya figura como revertido.
                if previo[1] == _REVERSION and previo[5] == original:
                    return
                raise ValueError(
                    f"el identificador {id!r} ya fue usado con otra operación"
                )
            objetivo = self._movimientos.get(original)
            if objetivo is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            _, tipo, origen, destino, cantidad, _ = objetivo
            if tipo == _REVERSION:
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            self._registrar((id, _REVERSION, destino, origen, cantidad, original))

    # -- internos ----------------------------------------------------------

    def _registrar(self, mov):
        """Aplica un movimiento ya validado; requiere el candado tomado.

        Todas las comprobaciones ocurren antes de la primera mutación, de modo
        que un rechazo deja el libro intacto.
        """
        id, _, origen, destino, cantidad, original = mov
        previo = self._movimientos.get(id)
        if previo is not None:
            if previo == mov:
                return  # repetición idempotente
            raise ValueError(
                f"el identificador {id!r} ya fue usado con otra operación"
            )

        saldos = self._saldos
        if origen is not None:
            disponible = saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: "
                    f"hay {disponible}, se necesitan {cantidad}"
                )
            saldos[origen] = disponible - cantidad
        if destino is not None:
            saldos[destino] = saldos.get(destino, 0) + cantidad
        self._movimientos[id] = mov
        self._historial.append(mov)
        if original is not None:
            self._revertidos.add(original)

    # El candado no se puede copiar ni serializar: se excluye del estado y se
    # recrea, para que copy/deepcopy/pickle sigan funcionando.

    def __getstate__(self):
        with self._candado:
            return {
                "_saldos": dict(self._saldos),
                "_movimientos": dict(self._movimientos),
                "_historial": list(self._historial),
                "_revertidos": set(self._revertidos),
            }

    def __setstate__(self, estado):
        self.__dict__.update(estado)
        self._candado = threading.RLock()
