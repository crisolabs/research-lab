"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._operaciones = {}
        self._revertidos = set()

    @staticmethod
    def _validar_id(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("El identificador debe ser un string no vacío")

    @staticmethod
    def _validar_ubicacion(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("La ubicación debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(valor):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_ubicacion(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _registrar(self, identificador, firma, movimiento, cambios):
        previo = self._operaciones.get(identificador)
        if previo is not None:
            if previo != firma:
                raise ValueError("El identificador ya fue usado con otros argumentos")
            return False
        # Aplicar el cambio únicamente después de validar la firma y el saldo.
        for ubicacion, delta in cambios:
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta
        self._operaciones[identificador] = firma
        self._historial.append(movimiento)
        return True

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        movimiento = {
            "id": id, "tipo": "ingreso", "origen": None,
            "destino": ubicacion, "cantidad": cantidad, "original": None,
        }
        self._registrar(id, firma, movimiento, ((ubicacion, cantidad),))
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        previo = self._operaciones.get(id)
        if previo is not None:
            if previo != firma:
                raise ValueError("El identificador ya fue usado con otros argumentos")
            return None
        if self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError("Saldo insuficiente")
        movimiento = {
            "id": id, "tipo": "retiro", "origen": ubicacion,
            "destino": None, "cantidad": cantidad, "original": None,
        }
        self._registrar(id, firma, movimiento, ((ubicacion, -cantidad),))
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(origen)
        self._validar_ubicacion(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        previo = self._operaciones.get(id)
        if previo is not None:
            if previo != firma:
                raise ValueError("El identificador ya fue usado con otros argumentos")
            return None
        if self._saldos.get(origen, 0) < cantidad:
            raise ValueError("Saldo insuficiente")
        movimiento = {
            "id": id, "tipo": "transferencia", "origen": origen,
            "destino": destino, "cantidad": cantidad, "original": None,
        }
        self._registrar(id, firma, movimiento,
                        ((origen, -cantidad), (destino, cantidad)))
        return None

    def revertir(self, id, original):
        self._validar_id(id)
        self._validar_id(original)
        firma = ("revertir", original)
        previo = self._operaciones.get(id)
        if previo is not None:
            if previo != firma:
                raise ValueError("El identificador ya fue usado con otros argumentos")
            return None

        movimiento_original = next(
            (m for m in self._historial if m["id"] == original), None
        )
        if movimiento_original is None or movimiento_original["tipo"] == "reversion":
            raise ValueError("El movimiento original no existe o no es reversible")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")

        tipo = movimiento_original["tipo"]
        origen = movimiento_original["origen"]
        destino = movimiento_original["destino"]
        cantidad = movimiento_original["cantidad"]
        cambios = []
        if tipo == "ingreso":
            cambios.append((destino, -cantidad))
        elif tipo == "retiro":
            cambios.append((origen, cantidad))
        else:
            cambios.extend(((destino, -cantidad), (origen, cantidad)))
        if any(self._saldos.get(ubicacion, 0) + delta < 0
               for ubicacion, delta in cambios):
            raise ValueError("La reversión dejaría un saldo negativo")

        movimiento = {
            "id": id, "tipo": "reversion", "origen": destino,
            "destino": origen, "cantidad": cantidad, "original": original,
        }
        self._registrar(id, firma, movimiento, cambios)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [movimiento.copy() for movimiento in self._historial]
