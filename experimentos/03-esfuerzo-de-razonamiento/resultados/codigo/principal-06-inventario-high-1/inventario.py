class Inventario:
    def __init__(self):
        self._estado = ({}, {}, set())

    @staticmethod
    def _validar_string(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad <= 0
        ):
            raise ValueError("La cantidad debe ser un entero positivo")

    def _es_repeticion(self, id, argumentos):
        movimientos = self._estado[1]
        if id not in movimientos:
            return False
        if movimientos[id][0] != argumentos:
            raise ValueError("El identificador ya corresponde a otro movimiento")
        return True

    def _aplicar(self, id, argumentos, tipo, origen, destino, cantidad, original=None):
        saldos, movimientos, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        if origen is not None:
            saldo = nuevos_saldos.get(origen, 0) - cantidad
            if saldo < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = saldo
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
        nuevos_movimientos[id] = (argumentos, registro)
        nuevos_revertidos = revertidos.copy()
        if original is not None:
            nuevos_revertidos.add(original)
        self._estado = (nuevos_saldos, nuevos_movimientos, nuevos_revertidos)

    def saldo(self, ubicacion):
        self._validar_string(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("ingreso", ubicacion, cantidad)
        if self._es_repeticion(id, argumentos):
            return
        self._aplicar(id, argumentos, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("retiro", ubicacion, cantidad)
        if self._es_repeticion(id, argumentos):
            return
        self._aplicar(id, argumentos, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_string(id)
        self._validar_string(origen)
        self._validar_string(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("Origen y destino deben ser distintos")
        argumentos = ("transferencia", origen, destino, cantidad)
        if self._es_repeticion(id, argumentos):
            return
        self._aplicar(id, argumentos, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_string(id)
        self._validar_string(original)
        argumentos = ("reversion", original)
        if self._es_repeticion(id, argumentos):
            return
        _, movimientos, revertidos = self._estado
        if original not in movimientos:
            raise ValueError("El movimiento original no existe")
        registro = movimientos[original][1]
        if registro["tipo"] == "reversion" or original in revertidos:
            raise ValueError("El movimiento no se puede revertir")
        self._aplicar(
            id,
            argumentos,
            "reversion",
            registro["destino"],
            registro["origen"],
            registro["cantidad"],
            original,
        )

    def historial(self):
        return [registro.copy() for _, registro in self._estado[1].values()]
