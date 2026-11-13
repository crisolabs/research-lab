"""Libro de inventario con historial e idempotencia."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = []
        self._por_id = {}
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
        previo = self._por_id.get(identificador)
        if previo is None:
            return False
        if previo != argumentos:
            raise ValueError("El identificador ya fue usado con otros argumentos")
        return True

    def _registrar(self, identificador, tipo, origen, destino, cantidad, argumentos, original=None):
        movimiento = {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        self._movimientos.append(movimiento)
        self._por_id[identificador] = argumentos

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, argumentos):
            return None

        self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
        self._registrar(id, "ingreso", None, ubicacion, cantidad, argumentos)
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
        self._registrar(id, "retiro", ubicacion, None, cantidad, argumentos)
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
        self._registrar(id, "transferencia", origen, destino, cantidad, argumentos)
        return None

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        argumentos = ("reversion", original)
        if self._repetido(id, argumentos):
            return None

        movimiento_original = None
        for movimiento in self._movimientos:
            if movimiento["id"] == original:
                movimiento_original = movimiento
                break
        if movimiento_original is None or movimiento_original["tipo"] == "reversion":
            raise ValueError("El movimiento original no se puede revertir")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")

        origen = movimiento_original["destino"]
        destino = movimiento_original["origen"]
        cantidad = movimiento_original["cantidad"]
        if origen is not None and self._saldos.get(origen, 0) < cantidad:
            raise ValueError("La reversión dejaría un saldo negativo")

        if origen is not None:
            self._saldos[origen] -= cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._registrar(id, "reversion", origen, destino, cantidad, argumentos, original)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [movimiento.copy() for movimiento in self._movimientos]
