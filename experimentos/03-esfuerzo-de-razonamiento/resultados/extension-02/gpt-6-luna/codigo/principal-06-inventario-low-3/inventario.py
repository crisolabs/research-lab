"""Libro de inventario con historial e idempotencia."""


class Inventario:
    """Registra movimientos de stock por ubicación."""

    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._historial = []
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("se requiere un string no vacío")

    @classmethod
    def _validar_cantidad(cls, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    @classmethod
    def _validar_id_y_ubicacion(cls, identificador, ubicacion):
        cls._validar_texto(identificador)
        cls._validar_texto(ubicacion)

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _aplicar(self, identificador, firma, registro, variaciones):
        previo = self._movimientos.get(identificador)
        if previo is not None:
            if previo["firma"] != firma:
                raise ValueError("el identificador ya se usó con otros argumentos")
            return None

        nuevos_saldos = {}
        for ubicacion, cambio in variaciones.items():
            nuevo = self._saldos.get(ubicacion, 0) + cambio
            if nuevo < 0:
                raise ValueError("saldo insuficiente")
            nuevos_saldos[ubicacion] = nuevo

        self._saldos.update(nuevos_saldos)
        self._movimientos[identificador] = {"firma": firma, "registro": registro}
        self._historial.append(registro)
        return None

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_id_y_ubicacion(id, ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        registro = {
            "id": id,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        return self._aplicar(id, firma, registro, {ubicacion: cantidad})

    def retirar(self, id, ubicacion, cantidad):
        self._validar_id_y_ubicacion(id, ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        registro = {
            "id": id,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        return self._aplicar(id, firma, registro, {ubicacion: -cantidad})

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        registro = {
            "id": id,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        return self._aplicar(
            id, firma, registro, {origen: -cantidad, destino: cantidad}
        )

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)

        previo = self._movimientos.get(id)
        if previo is not None:
            if previo["firma"] != firma:
                raise ValueError("el identificador ya se usó con otros argumentos")
            return None

        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError("el movimiento original no existe")
        original_registro = movimiento["registro"]
        if original_registro["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        origen = original_registro["destino"]
        destino = original_registro["origen"]
        cantidad = original_registro["cantidad"]
        registro = {
            "id": id,
            "tipo": "reversion",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

        variaciones = {}
        if original_registro["origen"] is not None:
            variaciones[original_registro["origen"]] = cantidad
        if original_registro["destino"] is not None:
            variaciones[original_registro["destino"]] = -cantidad

        # Comprobar todos los saldos antes de modificar cualquiera de ellos.
        nuevos_saldos = {}
        for ubicacion, cambio in variaciones.items():
            nuevo = self._saldos.get(ubicacion, 0) + cambio
            if nuevo < 0:
                raise ValueError("la reversión dejaría un saldo negativo")
            nuevos_saldos[ubicacion] = nuevo

        self._saldos.update(nuevos_saldos)
        self._movimientos[id] = {"firma": firma, "registro": registro}
        self._historial.append(registro)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [registro.copy() for registro in self._historial]
