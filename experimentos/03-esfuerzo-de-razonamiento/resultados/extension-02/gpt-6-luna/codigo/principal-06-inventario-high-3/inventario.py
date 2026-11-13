"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    """Mantiene saldos por ubicación y un historial de movimientos."""

    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._movimientos = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    @staticmethod
    def _registro(identificador, tipo, origen, destino, cantidad, original=None):
        return {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _ya_aplicado(self, identificador, argumentos):
        previo = self._movimientos.get(identificador)
        if previo is None:
            return False
        if previo["argumentos"] != argumentos:
            raise ValueError("El identificador ya se usó con otros argumentos")
        return True

    def _aplicar(self, identificador, argumentos, registro, cambios):
        """Aplica cambios ya validados y registra el movimiento."""
        for ubicacion, variacion in cambios.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + variacion
        self._historial.append(registro)
        self._movimientos[identificador] = {
            "argumentos": argumentos,
            "registro": registro,
        }

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("ingresar", ubicacion, cantidad)
        if self._ya_aplicado(identificador, argumentos):
            return None

        registro = self._registro(identificador, "ingreso", None, ubicacion, cantidad)
        self._aplicar(identificador, argumentos, registro, {ubicacion: cantidad})
        return None

    def retirar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        argumentos = ("retirar", ubicacion, cantidad)
        if self._ya_aplicado(identificador, argumentos):
            return None
        if self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError("Saldo insuficiente")

        registro = self._registro(identificador, "retiro", ubicacion, None, cantidad)
        self._aplicar(identificador, argumentos, registro, {ubicacion: -cantidad})
        return None

    def transferir(self, identificador, origen, destino, cantidad):
        self._validar_texto(identificador)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        argumentos = ("transferir", origen, destino, cantidad)
        if self._ya_aplicado(identificador, argumentos):
            return None
        if self._saldos.get(origen, 0) < cantidad:
            raise ValueError("Saldo insuficiente")

        registro = self._registro(identificador, "transferencia", origen, destino, cantidad)
        self._aplicar(
            identificador,
            argumentos,
            registro,
            {origen: -cantidad, destino: cantidad},
        )
        return None

    def revertir(self, identificador, original):
        self._validar_texto(identificador)
        self._validar_texto(original)
        argumentos = ("revertir", original)
        if self._ya_aplicado(identificador, argumentos):
            return None

        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        registro_original = movimiento["registro"]
        if registro_original["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")

        origen = registro_original["destino"]
        destino = registro_original["origen"]
        cantidad = registro_original["cantidad"]
        registro = self._registro(
            identificador, "reversion", origen, destino, cantidad, original
        )

        cambios = {}
        if origen is not None:
            cambios[origen] = cambios.get(origen, 0) - cantidad
        if destino is not None:
            cambios[destino] = cambios.get(destino, 0) + cantidad
        for ubicacion, variacion in cambios.items():
            if self._saldos.get(ubicacion, 0) + variacion < 0:
                raise ValueError("Saldo insuficiente para revertir")

        self._aplicar(identificador, argumentos, registro, cambios)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [registro.copy() for registro in self._historial]
