"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

_CLAVES = ("id", "tipo", "origen", "destino", "cantidad", "original")


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro
        self._historial = []
        self._revertidos = set()  # ids de movimientos ya revertidos
        self._lock = threading.RLock()

    # --- consultas ---

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        with self._lock:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._lock:
            return [dict(m) for m in self._historial]

    # --- mutaciones ---

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(id, "ingreso", None, ubicacion, cantidad, None)

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(id, "retiro", ubicacion, None, cantidad, None)

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar(id, "transferencia", origen, destino, cantidad, None)

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        with self._lock:
            existente = self._movimientos.get(id)
            if existente is not None:
                if existente["tipo"] == "reversion" and existente["original"] == original:
                    return None  # repetición idempotente
                raise ValueError(f"identificador ya usado con otros argumentos: {id!r}")
            previo = self._movimientos.get(original)
            if previo is None:
                raise ValueError(f"movimiento inexistente: {original!r}")
            if previo["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"movimiento ya revertido: {original!r}")
            self._aplicar(
                id,
                "reversion",
                previo["destino"],
                previo["origen"],
                previo["cantidad"],
                original,
            )
        return None

    # --- interno ---

    def _aplicar(self, id, tipo, origen, destino, cantidad, original):
        registro = dict(
            zip(_CLAVES, (id, tipo, origen, destino, cantidad, original))
        )
        with self._lock:
            existente = self._movimientos.get(id)
            if existente is not None:
                if existente == registro:
                    return None  # repetición idempotente
                raise ValueError(f"identificador ya usado con otros argumentos: {id!r}")
            if origen is not None and self._saldos.get(origen, 0) < cantidad:
                raise ValueError(f"saldo insuficiente en {origen!r}")
            # A partir de acá nada puede fallar: se aplica todo junto.
            if origen is not None:
                self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
            if destino is not None:
                self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
            self._movimientos[id] = registro
            self._historial.append(registro)
            if original is not None:
                self._revertidos.add(original)
        return None
