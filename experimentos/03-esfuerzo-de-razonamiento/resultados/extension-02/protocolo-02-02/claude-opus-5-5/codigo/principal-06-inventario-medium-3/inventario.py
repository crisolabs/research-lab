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
        self._movimientos = {}
        self._revertidos = set()

    # -- consultas ---------------------------------------------------------
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "ubicacion")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(m) for m in self._historial]

    # -- utilidades internas -----------------------------------------------
    def _ya_aplicado(self, id_, firma):
        """True si el id ya existe con la misma firma; ValueError si difiere."""
        previo = self._movimientos.get(id_)
        if previo is None:
            return False
        if previo[0] != firma:
            raise ValueError(f"identificador {id_!r} reutilizado con otros argumentos")
        return True

    def _aplicar(self, id_, firma, deltas, registro):
        nuevos = {}
        for ubic, delta in deltas:
            actual = nuevos.get(ubic, self._saldos.get(ubic, 0))
            nuevos[ubic] = actual + delta
        for ubic, valor in nuevos.items():
            if valor < 0:
                raise ValueError(f"saldo insuficiente en {ubic!r}")
        # A partir de aquí no hay excepciones posibles.
        self._saldos.update(nuevos)
        self._historial.append(registro)
        self._movimientos[id_] = (firma, len(self._historial) - 1)

    @staticmethod
    def _registro(id_, tipo, origen, destino, cantidad, original=None):
        return {
            "id": id_,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    # -- mutaciones --------------------------------------------------------
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(
            id, firma, [(ubicacion, cantidad)],
            self._registro(id, "ingreso", None, ubicacion, cantidad),
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
            id, firma, [(ubicacion, -cantidad)],
            self._registro(id, "retiro", ubicacion, None, cantidad),
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
            id, firma, [(origen, -cantidad), (destino, cantidad)],
            self._registro(id, "transferencia", origen, destino, cantidad),
        )
        return None

    def revertir(self, id, original):
        _validar_texto(id, "id")
        _validar_texto(original, "original")
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        previo = self._movimientos.get(original)
        if previo is None:
            raise ValueError(f"movimiento original {original!r} inexistente")
        mov = self._historial[previo[1]]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        cantidad = mov["cantidad"]
        origen, destino = mov["origen"], mov["destino"]
        deltas = []
        if destino is not None:
            deltas.append((destino, -cantidad))
        if origen is not None:
            deltas.append((origen, cantidad))
        self._aplicar(
            id, firma, deltas,
            self._registro(id, "reversion", destino, origen, cantidad, original),
        )
        self._revertidos.add(original)
        return None
