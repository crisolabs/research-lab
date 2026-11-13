class Inventario:
    def __init__(self):
        self._estado = ({}, {}, set())

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        self._aplicar(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        self._aplicar(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        movimiento = self._estado[1].get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        self._aplicar(
            id,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado[1].values()]

    def _aplicar(self, id, tipo, origen, destino, cantidad, original=None):
        saldos, movimientos, revertidos = self._estado
        movimiento = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        existente = movimientos.get(id)
        if existente is not None:
            if existente == movimiento:
                return
            raise ValueError("El identificador ya corresponde a otro movimiento")

        if original is not None:
            if movimientos[original]["tipo"] == "reversion":
                raise ValueError("No se puede revertir una reversión")
            if original in revertidos:
                raise ValueError("El movimiento ya fue revertido")

        if origen is not None and saldos.get(origen, 0) < cantidad:
            raise ValueError("Saldo insuficiente")

        nuevos_saldos = saldos.copy()
        if origen is not None:
            nuevos_saldos[origen] = nuevos_saldos.get(origen, 0) - cantidad
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad

        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = movimiento
        nuevos_revertidos = revertidos
        if original is not None:
            nuevos_revertidos = revertidos | {original}

        self._estado = (nuevos_saldos, nuevos_movimientos, nuevos_revertidos)
