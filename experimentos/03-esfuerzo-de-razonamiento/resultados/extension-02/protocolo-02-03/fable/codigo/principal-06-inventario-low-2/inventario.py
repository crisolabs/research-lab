"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro (el dict conserva el orden de aplicación)
        self._revertidos = set()
        self._lock = threading.RLock()

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        with self._lock:
            return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(id, "ingreso", None, ubicacion, int(cantidad), None)

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(id, "retiro", ubicacion, None, int(cantidad), None)

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar(id, "transferencia", origen, destino, int(cantidad), None)

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        with self._lock:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo["tipo"] == "reversion" and previo["original"] == original:
                    return
                raise ValueError(f"el identificador {id!r} ya fue usado con otros argumentos")
            mov = self._movimientos.get(original)
            if mov is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if mov["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            self._aplicar(id, "reversion", mov["destino"], mov["origen"], mov["cantidad"], original)
            self._revertidos.add(original)

    def historial(self):
        with self._lock:
            return [dict(m) for m in self._movimientos.values()]

    def _aplicar(self, id, tipo, origen, destino, cantidad, original):
        registro = {
            "id": str(id),
            "tipo": tipo,
            "origen": None if origen is None else str(origen),
            "destino": None if destino is None else str(destino),
            "cantidad": cantidad,
            "original": original,
        }
        with self._lock:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo == registro:
                    return
                raise ValueError(f"el identificador {id!r} ya fue usado con otros argumentos")
            if origen is not None and self._saldos.get(origen, 0) < cantidad:
                raise ValueError(f"saldo insuficiente en {origen!r}")
            if origen is not None:
                self._saldos[origen] -= cantidad
            if destino is not None:
                self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
            self._movimientos[id] = registro
