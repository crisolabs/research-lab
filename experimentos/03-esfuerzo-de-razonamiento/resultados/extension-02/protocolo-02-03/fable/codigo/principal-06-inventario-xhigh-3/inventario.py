"""Libro de inventario con movimientos idempotentes y reversibles."""


def _texto(valor, nombre):
    """Valida un string no vacío y lo devuelve como ``str`` exacto."""
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    # Normaliza subclases (p. ej. enums) para que hash e igualdad sean los de str.
    return str.__str__(valor)


def _cantidad(valor):
    """Valida un entero positivo no booleano y lo devuelve como ``int`` exacto."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("cantidad debe ser un entero positivo")
    return int.__index__(valor)


class Inventario:
    """Saldos por ubicación con un historial de movimientos identificados."""

    def __init__(self):
        self._saldos = {}
        # id -> registro; el orden de inserción es el orden de aplicación.
        self._movimientos = {}
        # Identificadores de movimientos que ya fueron revertidos.
        self._revertidos = set()

    def saldo(self, ubicacion):
        ubicacion = _texto(ubicacion, "ubicacion")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "id")
        ubicacion = _texto(ubicacion, "ubicacion")
        cantidad = _cantidad(cantidad)
        self._registrar(id, "ingreso", None, ubicacion, cantidad, None)

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "id")
        ubicacion = _texto(ubicacion, "ubicacion")
        cantidad = _cantidad(cantidad)
        self._registrar(id, "retiro", ubicacion, None, cantidad, None)

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "id")
        origen = _texto(origen, "origen")
        destino = _texto(destino, "destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._registrar(id, "transferencia", origen, destino, cantidad, None)

    def revertir(self, id, original):
        id = _texto(id, "id")
        original = _texto(original, "original")

        previo = self._movimientos.get(id)
        if previo is not None:
            if previo["tipo"] == "reversion" and previo["original"] == original:
                return None
            raise ValueError(f"identificador {id!r} ya usado con otros argumentos")

        base = self._movimientos.get(original)
        if base is None:
            raise ValueError(f"no existe el movimiento {original!r}")
        if base["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")

        self._registrar(
            id, "reversion", base["destino"], base["origen"], base["cantidad"], original
        )

    def historial(self):
        return [dict(registro) for registro in self._movimientos.values()]

    def _registrar(self, id, tipo, origen, destino, cantidad, original):
        """Aplica un movimiento ya validado: todo o nada, e idempotente por id."""
        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

        previo = self._movimientos.get(id)
        if previo is not None:
            if previo == registro:
                return None
            raise ValueError(f"identificador {id!r} ya usado con otros argumentos")

        # Se calculan todos los saldos nuevos antes de tocar el estado.
        nuevos = {}
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(f"saldo insuficiente en {origen!r}")
            nuevos[origen] = disponible - cantidad
        if destino is not None:
            nuevos[destino] = self._saldos.get(destino, 0) + cantidad

        self._saldos.update(nuevos)
        self._movimientos[id] = registro
        if original is not None:
            self._revertidos.add(original)
        return None
