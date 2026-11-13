class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._revertidos = set()

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

    def _es_repeticion(self, id, tipo, **argumentos):
        anterior = self._movimientos.get(id)
        if anterior is None:
            return False
        if anterior["tipo"] == tipo and all(
            anterior[campo] == valor for campo, valor in argumentos.items()
        ):
            return True
        raise ValueError("El identificador ya pertenece a otro movimiento")

    def _aplicar(self, id, tipo, origen, destino, cantidad, original=None):
        saldos = self._saldos.copy()
        if origen is not None:
            saldo = saldos.get(origen, 0) - cantidad
            if saldo < 0:
                raise ValueError("Saldo insuficiente")
            saldos[origen] = saldo
        if destino is not None:
            saldos[destino] = saldos.get(destino, 0) + cantidad

        movimientos = self._movimientos.copy()
        movimientos[id] = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        revertidos = self._revertidos
        if tipo == "reversion":
            revertidos = revertidos | {original}

        self._saldos, self._movimientos, self._revertidos = (
            saldos,
            movimientos,
            revertidos,
        )

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        if self._es_repeticion(id, "ingreso", destino=ubicacion, cantidad=cantidad):
            return
        self._aplicar(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        if self._es_repeticion(id, "retiro", origen=ubicacion, cantidad=cantidad):
            return
        self._aplicar(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        if self._es_repeticion(
            id, "transferencia", origen=origen, destino=destino, cantidad=cantidad
        ):
            return
        self._aplicar(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        if self._es_repeticion(id, "reversion", original=original):
            return
        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        if movimiento["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")
        self._aplicar(
            id,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._movimientos.values()]
