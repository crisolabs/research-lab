class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._historial = []
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío.")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad <= 0
        ):
            raise ValueError("La cantidad debe ser un entero positivo.")

    def _es_repetido(self, id, firma):
        anterior = self._movimientos.get(id)
        if anterior is None:
            return False
        if anterior[0] != firma:
            raise ValueError("El identificador ya corresponde a otra operación.")
        return True

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._es_repetido(id, firma):
            return
        self._aplicar(id, firma, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._es_repetido(id, firma):
            return
        self._aplicar(id, firma, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos.")
        firma = ("transferencia", origen, destino, cantidad)
        if self._es_repetido(id, firma):
            return
        self._aplicar(id, firma, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)
        if self._es_repetido(id, firma):
            return
        entrada = self._movimientos.get(original)
        if entrada is None:
            raise ValueError("El movimiento original no existe.")
        movimiento = entrada[1]
        if movimiento["tipo"] == "reversion" or original in self._revertidos:
            raise ValueError("El movimiento no se puede revertir.")
        self._aplicar(
            id,
            firma,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]

    def _aplicar(self, id, firma, tipo, origen, destino, cantidad, original=None):
        saldos = self._saldos.copy()
        if origen is not None:
            saldo = saldos.get(origen, 0) - cantidad
            if saldo < 0:
                raise ValueError("Saldo insuficiente.")
            saldos[origen] = saldo
        if destino is not None:
            saldos[destino] = saldos.get(destino, 0) + cantidad

        movimiento = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        movimientos = self._movimientos.copy()
        movimientos[id] = (firma, movimiento)
        historial = self._historial + [movimiento]
        revertidos = self._revertidos.copy()
        if original is not None:
            revertidos.add(original)

        self._saldos, self._movimientos, self._historial, self._revertidos = (
            saldos,
            movimientos,
            historial,
            revertidos,
        )
