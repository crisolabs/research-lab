"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = []
        self._por_id = {}
        self._argumentos = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _repetido(self, identificador, argumentos):
        if identificador not in self._argumentos:
            return False
        if self._argumentos[identificador] != argumentos:
            raise ValueError("El identificador ya se usó con otros argumentos")
        return True

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, argumentos):
            return None
        self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
        self._registrar(id, argumentos, "ingreso", None, ubicacion, cantidad, None)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("retiro", ubicacion, cantidad)
        if self._repetido(id, argumentos):
            return None
        if self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError("Saldo insuficiente")
        self._saldos[ubicacion] -= cantidad
        self._registrar(id, argumentos, "retiro", ubicacion, None, cantidad, None)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        argumentos = ("transferencia", origen, destino, cantidad)
        if self._repetido(id, argumentos):
            return None
        if self._saldos.get(origen, 0) < cantidad:
            raise ValueError("Saldo insuficiente")
        self._saldos[origen] -= cantidad
        self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._registrar(id, argumentos, "transferencia", origen, destino, cantidad, None)
        return None

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        argumentos = ("reversion", original)
        if self._repetido(id, argumentos):
            return None
        movimiento = self._por_id.get(original)
        if movimiento is None or movimiento["tipo"] == "reversion" or original in self._revertidos:
            raise ValueError("El movimiento no se puede revertir")

        tipo = movimiento["tipo"]
        origen, destino = movimiento["origen"], movimiento["destino"]
        cantidad = movimiento["cantidad"]
        rev_origen, rev_destino = destino, origen

        cambios = {}
        if tipo == "ingreso":
            cambios[destino] = self._saldos.get(destino, 0) - cantidad
        elif tipo == "retiro":
            cambios[origen] = self._saldos.get(origen, 0) + cantidad
        else:
            cambios[origen] = self._saldos.get(origen, 0) + cantidad
            cambios[destino] = self._saldos.get(destino, 0) - cantidad
        if any(valor < 0 for valor in cambios.values()):
            raise ValueError("La reversión dejaría un saldo negativo")

        self._saldos.update(cambios)
        self._revertidos.add(original)
        self._registrar(id, argumentos, "reversion", rev_origen, rev_destino, cantidad, original)
        return None

    def _registrar(self, identificador, argumentos, tipo, origen, destino, cantidad, original):
        movimiento = {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        self._argumentos[identificador] = argumentos
        self._por_id[identificador] = movimiento
        self._movimientos.append(movimiento)

    def historial(self):
        return [movimiento.copy() for movimiento in self._movimientos]
