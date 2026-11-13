class Inventario:
    def __init__(self):
        self._estado = ({}, {}, [], set())

    @staticmethod
    def _validar_string(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def _repetido(self, id, firma):
        movimientos = self._estado[1]
        if id not in movimientos:
            return False
        if movimientos[id][0] != firma:
            raise ValueError("El identificador ya corresponde a otro movimiento")
        return True

    def _aplicar(self, id, firma, registro, variaciones, revertido=None):
        if self._repetido(id, firma):
            return

        saldos, movimientos, historial, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        for ubicacion, variacion in variaciones:
            saldo = nuevos_saldos.get(ubicacion, 0) + variacion
            if saldo < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[ubicacion] = saldo

        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = (firma, registro)
        nuevo_historial = historial + [registro]
        nuevos_revertidos = revertidos.copy()
        if revertido is not None:
            nuevos_revertidos.add(revertido)
        self._estado = (
            nuevos_saldos, nuevos_movimientos, nuevo_historial, nuevos_revertidos
        )

    def saldo(self, ubicacion):
        self._validar_string(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(
            id,
            ("ingreso", ubicacion, cantidad),
            dict(id=id, tipo="ingreso", origen=None, destino=ubicacion,
                 cantidad=cantidad, original=None),
            [(ubicacion, cantidad)],
        )

    def retirar(self, id, ubicacion, cantidad):
        self._validar_string(id)
        self._validar_string(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(
            id,
            ("retiro", ubicacion, cantidad),
            dict(id=id, tipo="retiro", origen=ubicacion, destino=None,
                 cantidad=cantidad, original=None),
            [(ubicacion, -cantidad)],
        )

    def transferir(self, id, origen, destino, cantidad):
        self._validar_string(id)
        self._validar_string(origen)
        self._validar_string(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("Origen y destino deben ser distintos")
        self._aplicar(
            id,
            ("transferencia", origen, destino, cantidad),
            dict(id=id, tipo="transferencia", origen=origen, destino=destino,
                 cantidad=cantidad, original=None),
            [(origen, -cantidad), (destino, cantidad)],
        )

    def revertir(self, id, original):
        self._validar_string(id)
        self._validar_string(original)
        firma = ("reversion", original)
        if self._repetido(id, firma):
            return

        _, movimientos, _, revertidos = self._estado
        if original not in movimientos:
            raise ValueError("El movimiento original no existe")
        registro = movimientos[original][1]
        if registro["tipo"] == "reversion" or original in revertidos:
            raise ValueError("El movimiento no se puede revertir")

        origen = registro["destino"]
        destino = registro["origen"]
        cantidad = registro["cantidad"]
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        self._aplicar(
            id,
            firma,
            dict(id=id, tipo="reversion", origen=origen, destino=destino,
                 cantidad=cantidad, original=original),
            variaciones,
            revertido=original,
        )

    def historial(self):
        return [registro.copy() for registro in self._estado[2]]
