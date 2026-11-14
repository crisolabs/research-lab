"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"

_CLAVES = ("id", "tipo", "origen", "destino", "cantidad", "original")


class _TipoInvalido(ValueError, TypeError):
    """Argumento de tipo incorrecto: es un ValueError y también un TypeError."""


def _texto(valor, nombre):
    if not isinstance(valor, str):
        raise _TipoInvalido(f"{nombre} debe ser un string no vacío")
    if len(valor) == 0:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    # Normaliza subclases de str a un str exacto.
    return str.__str__(valor)


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _TipoInvalido("la cantidad debe ser un entero positivo")
    # Normaliza subclases de int a un int exacto.
    valor = int.__index__(valor)
    if valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


class Inventario:
    def __init__(self):
        self._saldos = {}
        # id -> (id, tipo, origen, destino, cantidad, original)
        self._movimientos = {}
        self._orden = []
        # id del movimiento original -> id de su reversión
        self._revertidos = {}
        self._candado = threading.RLock()

    # ------------------------------------------------------------ consultas

    def saldo(self, ubicacion):
        ubicacion = _texto(ubicacion, "la ubicación")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._candado:
            return [dict(zip(_CLAVES, registro)) for registro in self._orden]

    # ---------------------------------------------------------- movimientos

    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        self._aplicar((id, _INGRESO, None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        self._aplicar((id, _RETIRO, ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar((id, _TRANSFERENCIA, origen, destino, cantidad, None))

    def revertir(self, id, original):
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo[1] == _REVERSION and previo[5] == original:
                    return None
                raise ValueError(
                    f"el identificador {id!r} ya fue usado con otros argumentos"
                )
            movimiento = self._movimientos.get(original)
            if movimiento is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if movimiento[1] == _REVERSION:
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            _, _, origen, destino, cantidad, _ = movimiento
            self._aplicar((id, _REVERSION, destino, origen, cantidad, original))
        return None

    # -------------------------------------------------------------- interno

    def _aplicar(self, registro):
        """Aplica un registro ya validado: todo o nada."""
        id, tipo, origen, destino, cantidad, original = registro
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo == registro:
                    return
                raise ValueError(
                    f"el identificador {id!r} ya fue usado con otros argumentos"
                )

            # Se calculan los saldos nuevos sin tocar el estado.
            nuevos = {}
            if origen is not None:
                disponible = self._saldos.get(origen, 0)
                if disponible < cantidad:
                    raise ValueError(
                        f"saldo insuficiente en {origen!r}: "
                        f"hay {disponible}, se necesitan {cantidad}"
                    )
                nuevos[origen] = disponible - cantidad
            if destino is not None:
                nuevos[destino] = nuevos.get(
                    destino, self._saldos.get(destino, 0)
                ) + cantidad

            # A partir de acá no hay nada que pueda fallar por validación.
            self._saldos.update(nuevos)
            self._movimientos[id] = registro
            self._orden.append(registro)
            if original is not None:
                self._revertidos[original] = id
