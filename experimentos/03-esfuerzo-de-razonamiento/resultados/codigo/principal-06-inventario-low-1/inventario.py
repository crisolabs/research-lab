class Inventario:
    def __init__(self):
        self._estado = ({}, [], {}, set())

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

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(id, "ingreso", None, ubicacion, cantidad, None)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(id, "retiro", ubicacion, None, cantidad, None)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        self._aplicar(id, "transferencia", origen, destino, cantidad, None)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        operaciones = self._estado[2]
        if id in operaciones:
            anterior = operaciones[id]
            if anterior["tipo"] == "reversion" and anterior["original"] == original:
                return
            raise ValueError("El identificador ya tiene otros argumentos")
        movimiento = operaciones.get(original)
        if (movimiento is None or movimiento["tipo"] == "reversion"
                or original in self._estado[3]):
            raise ValueError("El movimiento no se puede revertir")
        self._aplicar(id, "reversion", movimiento["destino"],
                      movimiento["origen"], movimiento["cantidad"], original)

    def _aplicar(self, id, tipo, origen, destino, cantidad, original):
        saldos, historial, operaciones, revertidos = self._estado
        movimiento = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        if id in operaciones:
            if operaciones[id] == movimiento:
                return
            raise ValueError("El identificador ya tiene otros argumentos")
        nuevos_saldos = saldos.copy()
        if origen is not None:
            disponible = nuevos_saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = disponible - cantidad
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad
        nuevas_operaciones = operaciones.copy()
        nuevas_operaciones[id] = movimiento
        nuevos_revertidos = revertidos.copy()
        if original is not None:
            nuevos_revertidos.add(original)
        self._estado = (nuevos_saldos, historial + [movimiento],
                        nuevas_operaciones, nuevos_revertidos)

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado[1]]
