class Inventario:
    def __init__(self):
        self._estado = ({}, {}, (), frozenset())

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
        return self._estado[0].get(ubicacion, 0)

    def _repetido(self, identificador, firma):
        existente = self._estado[1].get(identificador)
        if existente is None:
            return False
        if existente[0] != firma:
            raise ValueError("El identificador ya corresponde a otro movimiento")
        return True

    def _aplicar(self, identificador, firma, registro, variaciones, original=None):
        saldos, movimientos, historial, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        for ubicacion, variacion in variaciones:
            nuevo_saldo = nuevos_saldos.get(ubicacion, 0) + variacion
            if nuevo_saldo < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[ubicacion] = nuevo_saldo
        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[identificador] = (firma, registro)
        nuevo_historial = historial + (registro,)
        nuevos_revertidos = revertidos
        if original is not None:
            nuevos_revertidos = revertidos | {original}
        self._estado = (
            nuevos_saldos,
            nuevos_movimientos,
            nuevo_historial,
            nuevos_revertidos,
        )

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, firma):
            return
        registro = (id, "ingreso", None, ubicacion, cantidad, None)
        self._aplicar(id, firma, registro, ((ubicacion, cantidad),))

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._repetido(id, firma):
            return
        registro = (id, "retiro", ubicacion, None, cantidad, None)
        self._aplicar(id, firma, registro, ((ubicacion, -cantidad),))

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._repetido(id, firma):
            return
        registro = (id, "transferencia", origen, destino, cantidad, None)
        self._aplicar(
            id, firma, registro, ((origen, -cantidad), (destino, cantidad))
        )

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)
        if self._repetido(id, firma):
            return
        movimiento = self._estado[1].get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        registro_original = movimiento[1]
        if registro_original[1] == "reversion" or original in self._estado[3]:
            raise ValueError("El movimiento no se puede revertir")
        origen = registro_original[3]
        destino = registro_original[2]
        cantidad = registro_original[4]
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        registro = (id, "reversion", origen, destino, cantidad, original)
        self._aplicar(id, firma, registro, variaciones, original)

    def historial(self):
        claves = ("id", "tipo", "origen", "destino", "cantidad", "original")
        return [dict(zip(claves, registro)) for registro in self._estado[2]]
