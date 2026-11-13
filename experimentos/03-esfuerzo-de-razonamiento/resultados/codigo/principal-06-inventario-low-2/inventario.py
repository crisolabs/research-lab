class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._historial = []
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

    def _repetido(self, id, argumentos):
        if id not in self._movimientos:
            return False
        if self._movimientos[id][0] != argumentos:
            raise ValueError("Identificador utilizado con otros argumentos")
        return True

    def _aplicar(self, id, argumentos, movimiento, variaciones, original=None):
        saldos = self._saldos.copy()
        for ubicacion, variacion in variaciones:
            saldo = saldos.get(ubicacion, 0) + variacion
            if saldo < 0:
                raise ValueError("Saldo insuficiente")
            saldos[ubicacion] = saldo
        movimientos = self._movimientos.copy()
        movimientos[id] = (argumentos, movimiento)
        historial = self._historial + [movimiento]
        revertidos = self._revertidos.copy()
        if original is not None:
            revertidos.add(original)
        self._saldos = saldos
        self._movimientos = movimientos
        self._historial = historial
        self._revertidos = revertidos

    def _registrar(self, id, tipo, origen, destino, cantidad):
        self._validar_texto(id)
        if origen is not None:
            self._validar_texto(origen)
        if destino is not None:
            self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if tipo == "transferencia" and origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        argumentos = (tipo, origen, destino, cantidad)
        if self._repetido(id, argumentos):
            return
        movimiento = dict(id=id, tipo=tipo, origen=origen, destino=destino,
                          cantidad=cantidad, original=None)
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        self._aplicar(id, argumentos, movimiento, variaciones)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(ubicacion)
        self._registrar(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(ubicacion)
        self._registrar(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._registrar(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        argumentos = ("reversion", original)
        if self._repetido(id, argumentos):
            return
        if original not in self._movimientos:
            raise ValueError("Movimiento original inexistente")
        anterior = self._movimientos[original][1]
        if anterior["tipo"] == "reversion" or original in self._revertidos:
            raise ValueError("El movimiento no se puede revertir")
        origen = anterior["destino"]
        destino = anterior["origen"]
        cantidad = anterior["cantidad"]
        movimiento = dict(id=id, tipo="reversion", origen=origen,
                          destino=destino, cantidad=cantidad, original=original)
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        self._aplicar(id, argumentos, movimiento, variaciones, original)

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]
