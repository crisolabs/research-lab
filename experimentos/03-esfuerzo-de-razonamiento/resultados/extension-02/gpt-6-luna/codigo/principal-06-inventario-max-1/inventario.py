class Inventario:
    def __init__(self):
        self._estado = ({}, {}, {}, set(), [])

    @property
    def _saldos(self):
        return self._estado[0]

    @property
    def _firmas(self):
        return self._estado[1]

    @property
    def _movimientos(self):
        return self._estado[2]

    @property
    def _revertidos(self):
        return self._estado[3]

    @property
    def _historial(self):
        return self._estado[4]

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def _es_repeticion(self, identificador, firma):
        if identificador not in self._firmas:
            return False
        if self._firmas[identificador] != firma:
            raise ValueError("El identificador ya fue usado con otros argumentos")
        return True

    def _registrar(self, identificador, firma, movimiento, cambios, original=None):
        movimiento = dict(movimiento)
        saldos = self._saldos.copy()
        firmas = self._firmas.copy()
        movimientos = self._movimientos.copy()
        revertidos = self._revertidos.copy()
        historial = self._historial.copy()

        for ubicacion, saldo in cambios.items():
            saldos[ubicacion] = saldo
        firmas[identificador] = firma
        movimientos[identificador] = movimiento
        historial.append(movimiento)
        if original is not None:
            revertidos.add(original)
        self._estado = (saldos, firmas, movimientos, revertidos, historial)

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        nuevo_saldo = self._saldos.get(ubicacion, 0) + cantidad
        movimiento = {
            "id": identificador,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(identificador, firma, movimiento, {ubicacion: nuevo_saldo})
        return None

    def retirar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        saldo_actual = self._saldos.get(ubicacion, 0)
        if saldo_actual < cantidad:
            raise ValueError("Saldo insuficiente")
        movimiento = {
            "id": identificador,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(
            identificador, firma, movimiento, {ubicacion: saldo_actual - cantidad}
        )
        return None

    def transferir(self, identificador, origen, destino, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        saldo_origen = self._saldos.get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("Saldo insuficiente")
        saldo_destino = self._saldos.get(destino, 0)
        movimiento = {
            "id": identificador,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(
            identificador,
            firma,
            movimiento,
            {origen: saldo_origen - cantidad, destino: saldo_destino + cantidad},
        )
        return None

    def revertir(self, identificador, original):
        self._validar_texto(identificador)
        self._validar_texto(original)
        firma = ("revertir", original)
        if self._es_repeticion(identificador, firma):
            return None
        if original not in self._movimientos:
            raise ValueError("El movimiento original no existe")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")

        movimiento_original = self._movimientos[original]
        tipo = movimiento_original["tipo"]
        if tipo == "reversion":
            raise ValueError("No se puede revertir una reversión")

        origen = movimiento_original["destino"]
        destino = movimiento_original["origen"]
        cantidad = movimiento_original["cantidad"]
        cambios = {}

        if origen is not None:
            saldo_origen = self._saldos.get(origen, 0)
            if saldo_origen < cantidad:
                raise ValueError("Saldo insuficiente")
            cambios[origen] = saldo_origen - cantidad
        if destino is not None:
            cambios[destino] = self._saldos.get(destino, 0) + cantidad

        movimiento = {
            "id": identificador,
            "tipo": "reversion",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        self._registrar(identificador, firma, movimiento, cambios, original)
        return None

    def historial(self):
        return [dict(movimiento) for movimiento in self._historial]
