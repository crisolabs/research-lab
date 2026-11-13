"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    """Mantiene saldos por ubicación y un historial de movimientos."""

    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._movimientos = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo no booleano")

    def _repetido(self, identificador, firma):
        previo = self._movimientos.get(identificador)
        if previo is None:
            return False
        if previo["firma"] != firma:
            raise ValueError("el identificador ya fue usado con otros argumentos")
        return True

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None

        nuevo_saldo = self._saldos.get(ubicacion, 0) + cantidad
        registro = {
            "id": id,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._saldos[ubicacion] = nuevo_saldo
        self._registrar(registro, firma)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(ubicacion, "ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None
        saldo_actual = self._saldos.get(ubicacion, 0)
        if saldo_actual < cantidad:
            raise ValueError("saldo insuficiente")

        registro = {
            "id": id,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._saldos[ubicacion] = saldo_actual - cantidad
        self._registrar(registro, firma)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "identificador")
        self._validar_texto(origen, "origen")
        self._validar_texto(destino, "destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._repetido(id, firma):
            return None
        saldo_origen = self._saldos.get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("saldo insuficiente")

        registro = {
            "id": id,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        nuevo_origen = saldo_origen - cantidad
        nuevo_destino = self._saldos.get(destino, 0) + cantidad
        self._saldos[origen] = nuevo_origen
        self._saldos[destino] = nuevo_destino
        self._registrar(registro, firma)
        return None

    def revertir(self, id, original):
        self._validar_texto(id, "identificador")
        self._validar_texto(original, "identificador original")
        firma = ("reversion", original)
        if self._repetido(id, firma):
            return None

        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError("el movimiento original no existe")
        if movimiento["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        tipo = movimiento["tipo"]
        origen = movimiento["origen"]
        destino = movimiento["destino"]
        cantidad = movimiento["cantidad"]
        nuevo_origen = destino
        nuevo_destino = origen

        # Calcular todos los saldos antes de mutar para que la reversión sea atómica.
        cambios = {}
        if nuevo_origen is not None:
            cambios[nuevo_origen] = self._saldos.get(nuevo_origen, 0) - cantidad
        if nuevo_destino is not None:
            cambios[nuevo_destino] = self._saldos.get(nuevo_destino, 0) + cantidad
        if any(saldo < 0 for saldo in cambios.values()):
            raise ValueError("la reversión dejaría un saldo negativo")

        registro = {
            "id": id,
            "tipo": "reversion",
            "origen": nuevo_origen,
            "destino": nuevo_destino,
            "cantidad": cantidad,
            "original": original,
        }
        for ubicacion, saldo in cambios.items():
            self._saldos[ubicacion] = saldo
        self._registrar(registro, firma)
        self._revertidos.add(original)
        return None

    def _registrar(self, registro, firma):
        self._historial.append(registro)
        self._movimientos[registro["id"]] = {
            "firma": firma,
            "tipo": registro["tipo"],
            "origen": registro["origen"],
            "destino": registro["destino"],
            "cantidad": registro["cantidad"],
        }

    def historial(self):
        return [registro.copy() for registro in self._historial]
