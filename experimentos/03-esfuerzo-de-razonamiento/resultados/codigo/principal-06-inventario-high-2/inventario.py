class Inventario:
    def __init__(self):
        self._estado = ({}, [], {}, frozenset())

    @staticmethod
    def _validar_string(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (not isinstance(cantidad, int)
                or isinstance(cantidad, bool)
                or cantidad <= 0):
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_string(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        solicitud = ("ingreso", ubicacion, cantidad)
        if self._es_repeticion(id, solicitud):
            return
        self._registrar(id, solicitud, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        solicitud = ("retiro", ubicacion, cantidad)
        if self._es_repeticion(id, solicitud):
            return
        self._registrar(id, solicitud, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_string(id)
        self._validar_string(origen)
        self._validar_string(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        solicitud = ("transferencia", origen, destino, cantidad)
        if self._es_repeticion(id, solicitud):
            return
        self._registrar(id, solicitud, "transferencia", origen, destino,
                        cantidad)

    def revertir(self, id, original):
        self._validar_string(id)
        self._validar_string(original)
        solicitud = ("reversion", original)
        if self._es_repeticion(id, solicitud):
            return
        movimientos, revertidos = self._estado[2:]
        if original not in movimientos:
            raise ValueError("El movimiento original no existe")
        registro = movimientos[original][1]
        if registro["tipo"] == "reversion" or original in revertidos:
            raise ValueError("El movimiento no se puede revertir")
        self._registrar(id, solicitud, "reversion", registro["destino"],
                        registro["origen"], registro["cantidad"], original)

    def historial(self):
        return [registro.copy() for registro in self._estado[1]]

    def _es_repeticion(self, id, solicitud):
        movimiento = self._estado[2].get(id)
        if movimiento is None:
            return False
        if movimiento[0] != solicitud:
            raise ValueError("El identificador ya se usó con otros argumentos")
        return True

    def _registrar(self, id, solicitud, tipo, origen, destino, cantidad,
                   original=None):
        saldos, historial, movimientos, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        if origen is not None:
            disponible = nuevos_saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = disponible - cantidad
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad
        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = (solicitud, registro)
        nuevos_revertidos = revertidos
        if original is not None:
            nuevos_revertidos = revertidos | {original}
        self._estado = (nuevos_saldos, historial + [registro],
                        nuevos_movimientos, nuevos_revertidos)
