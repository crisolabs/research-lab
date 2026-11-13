"""Libro de movimientos de inventario."""


class Inventario:
    """Mantiene saldos y un historial idempotente de movimientos."""

    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._revertidos = set()
        self._historial = []

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "id")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._es_repeticion(id, firma):
            return

        movimiento = {
            "id": id,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, firma, movimiento, {ubicacion: cantidad})

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "id")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._es_repeticion(id, firma):
            return
        if self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError("saldo insuficiente")

        movimiento = {
            "id": id,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, firma, movimiento, {ubicacion: -cantidad})

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "id")
        self._validar_texto(origen, "origen")
        self._validar_texto(destino, "destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._es_repeticion(id, firma):
            return
        if self._saldos.get(origen, 0) < cantidad:
            raise ValueError("saldo insuficiente")

        movimiento = {
            "id": id,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, firma, movimiento, {origen: -cantidad, destino: cantidad})

    def revertir(self, id, original):
        self._validar_texto(id, "id")
        self._validar_texto(original, "original")
        firma = ("reversion", original)
        if self._es_repeticion(id, firma):
            return

        movimiento_original = self._movimientos.get(original)
        if movimiento_original is None:
            raise ValueError("movimiento original inexistente")
        if movimiento_original["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        registro = movimiento_original
        cantidad = registro["cantidad"]
        origen = registro["destino"]
        destino = registro["origen"]
        deltas = {}
        if origen is not None:
            deltas[origen] = deltas.get(origen, 0) - cantidad
        if destino is not None:
            deltas[destino] = deltas.get(destino, 0) + cantidad
        for ubicacion, delta in deltas.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError("la reversión dejaría un saldo negativo")

        movimiento = {
            "id": id,
            "tipo": "reversion",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        self._aplicar(id, firma, movimiento, deltas)
        self._revertidos.add(original)

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]

    def _es_repeticion(self, id, firma):
        existente = self._movimientos.get(id)
        if existente is None:
            return False
        if existente["firma"] != firma:
            raise ValueError("el identificador ya se usó con otros argumentos")
        return True

    def _aplicar(self, id, firma, movimiento, deltas):
        for ubicacion, delta in deltas.items():
            saldo = self._saldos.get(ubicacion, 0) + delta
            if saldo:
                self._saldos[ubicacion] = saldo
            else:
                self._saldos.pop(ubicacion, None)
        self._movimientos[id] = {"firma": firma, **movimiento}
        self._historial.append(movimiento)
