"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> (firma de la operación, índice en historial)
        self._ids = {}
        self._revertidos = set()

    # ------------------------------------------------------------ consultas
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "ubicacion")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(m) for m in self._historial]

    # ------------------------------------------------------------ internos
    def _ya_aplicado(self, id, firma):
        """True si el id ya fue aplicado con la misma firma; error si difiere."""
        previo = self._ids.get(id)
        if previo is None:
            return False
        if previo != firma:
            raise ValueError(f"identificador {id!r} reutilizado con otros argumentos")
        return True

    def _aplicar(self, id, firma, variaciones, movimiento):
        # Validar que ningún saldo quede negativo antes de aplicar.
        nuevos = {}
        for ubicacion, delta in variaciones:
            actual = nuevos.get(ubicacion, self._saldos.get(ubicacion, 0))
            nuevos[ubicacion] = actual + delta
        for ubicacion, valor in nuevos.items():
            if valor < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")
        self._saldos.update(nuevos)
        self._ids[id] = firma
        self._historial.append(movimiento)

    @staticmethod
    def _movimiento(id, tipo, origen, destino, cantidad, original=None):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    # ------------------------------------------------------------ mutaciones
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(
            id,
            firma,
            [(ubicacion, cantidad)],
            self._movimiento(id, "ingreso", None, ubicacion, cantidad),
        )
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(
            id,
            firma,
            [(ubicacion, -cantidad)],
            self._movimiento(id, "retiro", ubicacion, None, cantidad),
        )
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "id")
        _validar_texto(origen, "origen")
        _validar_texto(destino, "destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(
            id,
            firma,
            [(origen, -cantidad), (destino, cantidad)],
            self._movimiento(id, "transferencia", origen, destino, cantidad),
        )
        return None

    def revertir(self, id, original):
        _validar_texto(id, "id")
        _validar_texto(original, "original")
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        if original not in self._ids:
            raise ValueError(f"movimiento original {original!r} inexistente")
        base = next(m for m in self._historial if m["id"] == original)
        if base["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")

        cantidad = base["cantidad"]
        origen, destino = base["destino"], base["origen"]
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))

        self._aplicar(
            id,
            firma,
            variaciones,
            self._movimiento(id, "reversion", origen, destino, cantidad, original),
        )
        self._revertidos.add(original)
        return None
