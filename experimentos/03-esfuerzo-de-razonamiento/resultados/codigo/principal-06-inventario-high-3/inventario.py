class Inventario:
    def __init__(self):
        self._estado = ({}, {}, frozenset())

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (not isinstance(cantidad, int)
                or isinstance(cantidad, bool)
                or cantidad <= 0):
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def _es_repeticion(self, id, movimiento):
        anterior = self._estado[1].get(id)
        if anterior is None:
            return False
        if anterior != movimiento:
            raise ValueError("El identificador ya tiene otros argumentos")
        return True

    def _aplicar(self, id, movimiento, original_revertido=None):
        saldos, movimientos, revertidos = self._estado
        _, origen, destino, cantidad, _ = movimiento
        nuevos_saldos = saldos.copy()
        if origen is not None:
            restante = nuevos_saldos.get(origen, 0) - cantidad
            if restante < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = restante
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad
        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = movimiento
        if original_revertido is not None:
            revertidos = revertidos.union((original_revertido,))
        self._estado = (nuevos_saldos, nuevos_movimientos, revertidos)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        movimiento = ("ingreso", None, ubicacion, cantidad, None)
        if not self._es_repeticion(id, movimiento):
            self._aplicar(id, movimiento)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        movimiento = ("retiro", ubicacion, None, cantidad, None)
        if not self._es_repeticion(id, movimiento):
            self._aplicar(id, movimiento)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        movimiento = ("transferencia", origen, destino, cantidad, None)
        if not self._es_repeticion(id, movimiento):
            self._aplicar(id, movimiento)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        _, movimientos, revertidos = self._estado
        anterior = movimientos.get(id)
        if anterior is not None:
            if anterior[0] == "reversion" and anterior[4] == original:
                return
            raise ValueError("El identificador ya tiene otros argumentos")
        movimiento = movimientos.get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        tipo, origen, destino, cantidad, _ = movimiento
        if tipo == "reversion" or original in revertidos:
            raise ValueError("El movimiento no se puede revertir")
        reversion = ("reversion", destino, origen, cantidad, original)
        self._aplicar(id, reversion, original_revertido=original)

    def historial(self):
        claves = ("id", "tipo", "origen", "destino", "cantidad", "original")
        return [
            dict(zip(claves, (id,) + movimiento))
            for id, movimiento in self._estado[1].items()
        ]
