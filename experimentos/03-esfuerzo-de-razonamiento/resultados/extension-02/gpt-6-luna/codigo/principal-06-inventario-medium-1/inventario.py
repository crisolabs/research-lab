"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._por_id = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def _registrar(self, movimiento, firma):
        identificador = movimiento["id"]
        self._por_id[identificador] = (firma, movimiento)
        self._historial.append(movimiento)

    def _repetido(self, identificador, firma):
        anterior = self._por_id.get(identificador)
        if anterior is None:
            return False
        if anterior[0] != firma:
            raise ValueError("el identificador ya se usó con otros argumentos")
        return True

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None
        self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
        self._registrar({"id": id, "tipo": "ingreso", "origen": None,
                         "destino": ubicacion, "cantidad": cantidad, "original": None}, firma)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None
        saldo = self._saldos.get(ubicacion, 0)
        if saldo < cantidad:
            raise ValueError("saldo insuficiente")
        self._saldos[ubicacion] = saldo - cantidad
        self._registrar({"id": id, "tipo": "retiro", "origen": ubicacion,
                         "destino": None, "cantidad": cantidad, "original": None}, firma)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(origen, "origen")
        self._validar_texto(destino, "destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if self._repetido(id, firma):
            return None
        saldo = self._saldos.get(origen, 0)
        if saldo < cantidad:
            raise ValueError("saldo insuficiente")
        self._saldos[origen] = saldo - cantidad
        self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._registrar({"id": id, "tipo": "transferencia", "origen": origen,
                         "destino": destino, "cantidad": cantidad, "original": None}, firma)

    def revertir(self, id, original):
        self._validar_texto(id, "identificador")
        self._validar_texto(original, "identificador original")
        firma = ("revertir", original)
        if self._repetido(id, firma):
            return None
        registro = self._por_id.get(original)
        if registro is None:
            raise ValueError("movimiento original inexistente")
        movimiento = registro[1]
        if movimiento["tipo"] == "reversion" or original in self._revertidos:
            raise ValueError("el movimiento no se puede revertir")

        tipo = movimiento["tipo"]
        origen, destino = movimiento["origen"], movimiento["destino"]
        cantidad = movimiento["cantidad"]
        cambios = {}
        if tipo == "ingreso":
            cambios[destino] = self._saldos.get(destino, 0) - cantidad
        elif tipo == "retiro":
            cambios[origen] = self._saldos.get(origen, 0) + cantidad
        else:
            cambios[origen] = self._saldos.get(origen, 0) + cantidad
            cambios[destino] = self._saldos.get(destino, 0) - cantidad
        if any(saldo < 0 for saldo in cambios.values()):
            raise ValueError("la reversión dejaría un saldo negativo")

        for ubicacion, saldo in cambios.items():
            self._saldos[ubicacion] = saldo
        reverso = {"id": id, "tipo": "reversion", "origen": destino,
                   "destino": origen, "cantidad": cantidad, "original": original}
        self._registrar(reverso, firma)
        self._revertidos.add(original)

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]
