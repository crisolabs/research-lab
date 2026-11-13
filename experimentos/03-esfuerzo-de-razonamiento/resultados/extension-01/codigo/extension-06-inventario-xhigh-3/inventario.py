class Inventario:
    def __init__(self):
        self._estado = ({}, [], {}, set())

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("La ubicación o el identificador debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._mover(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._mover(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._mover(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)
        if self._es_repeticion(id, firma):
            return

        existente = self._estado[2].get(original)
        if existente is None:
            raise ValueError("El movimiento original no existe")
        movimiento = existente[1]
        if movimiento["tipo"] == "reversion" or original in self._estado[3]:
            raise ValueError("El movimiento no se puede revertir")

        self._aplicar(
            firma,
            {
                "id": id,
                "tipo": "reversion",
                "origen": movimiento["destino"],
                "destino": movimiento["origen"],
                "cantidad": movimiento["cantidad"],
                "original": original,
            },
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado[1]]

    def _es_repeticion(self, id, firma):
        existente = self._estado[2].get(id)
        if existente is None:
            return False
        if existente[0] != firma:
            raise ValueError("El identificador ya se usó con otros argumentos")
        return True

    def _mover(self, id, tipo, origen, destino, cantidad):
        self._validar_texto(id)
        if tipo != "ingreso":
            self._validar_texto(origen)
        if tipo != "retiro":
            self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if tipo == "transferencia" and origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")

        firma = (tipo, origen, destino, cantidad)
        if self._es_repeticion(id, firma):
            return
        self._aplicar(
            firma,
            {
                "id": id,
                "tipo": tipo,
                "origen": origen,
                "destino": destino,
                "cantidad": cantidad,
                "original": None,
            },
        )

    def _aplicar(self, firma, movimiento):
        saldos, historial, movimientos, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        origen = movimiento["origen"]
        destino = movimiento["destino"]
        cantidad = movimiento["cantidad"]
        if origen is not None:
            restante = nuevos_saldos.get(origen, 0) - cantidad
            if restante < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = restante
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad

        nuevo_historial = historial + [movimiento]
        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[movimiento["id"]] = (firma, movimiento)
        nuevos_revertidos = revertidos.copy()
        if movimiento["original"] is not None:
            nuevos_revertidos.add(movimiento["original"])
        self._estado = (
            nuevos_saldos,
            nuevo_historial,
            nuevos_movimientos,
            nuevos_revertidos,
        )
