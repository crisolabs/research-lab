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
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad <= 0
        ):
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        saldos, _, _ = self._estado
        return saldos.get(ubicacion, 0)

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
        _, movimientos, _ = self._estado
        movimiento = movimientos.get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        if movimiento["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        self._aplicar(
            id,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self):
        _, movimientos, _ = self._estado
        return [movimiento.copy() for movimiento in movimientos.values()]

    def _aplicar(self, id, tipo, origen, destino, cantidad, original):
        saldos, movimientos, revertidos = self._estado
        movimiento = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        anterior = movimientos.get(id)
        if anterior is not None:
            if anterior == movimiento:
                return
            raise ValueError("El identificador ya tiene otros argumentos")
        if original is not None and original in revertidos:
            raise ValueError("El movimiento original ya fue revertido")

        nuevos_saldos = saldos.copy()
        if origen is not None:
            saldo_origen = saldos.get(origen, 0) - cantidad
            if saldo_origen < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = saldo_origen
        if destino is not None:
            nuevos_saldos[destino] = saldos.get(destino, 0) + cantidad

        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = movimiento
        nuevos_revertidos = revertidos.copy()
        if original is not None:
            nuevos_revertidos.add(original)
        self._estado = (nuevos_saldos, nuevos_movimientos, nuevos_revertidos)
