class Inventario:
    def __init__(self):
        self._estado = ({}, {}, set())

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad <= 0
        ):
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "La ubicación")
        return self._estado[0].get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "El identificador")
        self._validar_texto(ubicacion, "La ubicación")
        self._validar_cantidad(cantidad)
        self._registrar(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "El identificador")
        self._validar_texto(ubicacion, "La ubicación")
        self._validar_cantidad(cantidad)
        self._registrar(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "El identificador")
        self._validar_texto(origen, "El origen")
        self._validar_texto(destino, "El destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        self._registrar(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id, "El identificador")
        self._validar_texto(original, "El identificador original")
        movimiento = self._estado[1].get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        if movimiento["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        self._registrar(
            id,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado[1].values()]

    def _registrar(self, id, tipo, origen, destino, cantidad, original=None):
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
            if anterior != movimiento:
                raise ValueError("El identificador ya tiene otra operación")
            return
        if original is not None and original in revertidos:
            raise ValueError("El movimiento original ya fue revertido")

        nuevos_saldos = saldos.copy()
        if origen is not None:
            disponible = nuevos_saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[origen] = disponible - cantidad
        if destino is not None:
            nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad

        nuevos_movimientos = movimientos.copy()
        nuevos_movimientos[id] = movimiento
        nuevos_revertidos = revertidos.copy()
        if original is not None:
            nuevos_revertidos.add(original)
        self._estado = (nuevos_saldos, nuevos_movimientos, nuevos_revertidos)
