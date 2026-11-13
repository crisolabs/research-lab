class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._historial = []
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    @staticmethod
    def _nuevo_movimiento(identificador, tipo, origen, destino, cantidad, original=None):
        return {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _es_idempotente_o_conflicto(self, identificador, firma):
        anterior = self._movimientos.get(identificador)
        if anterior is None:
            return False
        if anterior["firma"] == firma:
            return True
        raise ValueError("el identificador ya se usó con otra operación")

    def _registrar(self, identificador, firma, movimiento):
        self._movimientos[identificador] = {"firma": firma, "movimiento": movimiento}
        self._historial.append(movimiento)

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._es_idempotente_o_conflicto(id, firma):
            return None

        nuevo_saldo = self._saldos.get(ubicacion, 0) + cantidad
        movimiento = self._nuevo_movimiento(id, "ingreso", None, ubicacion, cantidad)
        self._saldos[ubicacion] = nuevo_saldo
        self._registrar(id, firma, movimiento)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._es_idempotente_o_conflicto(id, firma):
            return None

        saldo_actual = self._saldos.get(ubicacion, 0)
        if saldo_actual < cantidad:
            raise ValueError("saldo insuficiente")

        movimiento = self._nuevo_movimiento(id, "retiro", ubicacion, None, cantidad)
        self._saldos[ubicacion] = saldo_actual - cantidad
        self._registrar(id, firma, movimiento)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(origen, "el origen")
        self._validar_texto(destino, "el destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._es_idempotente_o_conflicto(id, firma):
            return None

        saldo_origen = self._saldos.get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("saldo insuficiente")

        nuevo_saldo_origen = saldo_origen - cantidad
        nuevo_saldo_destino = self._saldos.get(destino, 0) + cantidad
        movimiento = self._nuevo_movimiento(
            id, "transferencia", origen, destino, cantidad
        )
        self._saldos[origen] = nuevo_saldo_origen
        self._saldos[destino] = nuevo_saldo_destino
        self._registrar(id, firma, movimiento)
        return None

    def revertir(self, id, original):
        self._validar_texto(id, "el identificador")
        self._validar_texto(original, "el identificador original")
        firma = ("reversion", original)
        if self._es_idempotente_o_conflicto(id, firma):
            return None

        registro_original = self._movimientos.get(original)
        if registro_original is None:
            raise ValueError("el movimiento original no existe")
        movimiento_original = registro_original["movimiento"]
        if movimiento_original["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        tipo_original = movimiento_original["tipo"]
        origen = movimiento_original["origen"]
        destino = movimiento_original["destino"]
        cantidad = movimiento_original["cantidad"]

        if tipo_original == "ingreso":
            ubicacion = destino
            saldo_actual = self._saldos.get(ubicacion, 0)
            if saldo_actual < cantidad:
                raise ValueError("la reversión dejaría un saldo negativo")
            cambios = {ubicacion: saldo_actual - cantidad}
            origen_reversion, destino_reversion = ubicacion, None
        elif tipo_original == "retiro":
            cambios = {origen: self._saldos.get(origen, 0) + cantidad}
            origen_reversion, destino_reversion = None, origen
        else:
            saldo_destino = self._saldos.get(destino, 0)
            if saldo_destino < cantidad:
                raise ValueError("la reversión dejaría un saldo negativo")
            cambios = {
                origen: self._saldos.get(origen, 0) + cantidad,
                destino: saldo_destino - cantidad,
            }
            origen_reversion, destino_reversion = destino, origen

        movimiento = self._nuevo_movimiento(
            id,
            "reversion",
            origen_reversion,
            destino_reversion,
            cantidad,
            original,
        )
        self._saldos.update(cambios)
        self._registrar(id, firma, movimiento)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]
