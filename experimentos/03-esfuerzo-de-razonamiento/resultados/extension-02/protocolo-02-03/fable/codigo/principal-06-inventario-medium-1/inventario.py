"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

_CLAVES = ("id", "tipo", "origen", "destino", "cantidad", "original")


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return int(cantidad)


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro
        self._historial = []
        self._revertidos = set()  # ids de movimientos ya revertidos
        self._candado = threading.RLock()

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._candado:
            return [dict(m) for m in self._historial]

    # ------------------------------------------------------------------ #
    # Mutaciones
    # ------------------------------------------------------------------ #
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "ingreso", None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "retiro", ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        cantidad = _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar(
            self._registro(id, "transferencia", origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo["tipo"] == "reversion" and previo["original"] == original:
                    return None
                raise ValueError(f"identificador ya usado con otros argumentos: {id!r}")
            base = self._movimientos.get(original)
            if base is None:
                raise ValueError(f"movimiento inexistente: {original!r}")
            if base["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"movimiento ya revertido: {original!r}")
            self._aplicar(
                self._registro(
                    id,
                    "reversion",
                    base["destino"],
                    base["origen"],
                    base["cantidad"],
                    original,
                )
            )
        return None

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #
    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original):
        return dict(zip(_CLAVES, (id, tipo, origen, destino, cantidad, original)))

    def _aplicar(self, registro):
        """Aplica el registro de forma atómica: valida todo antes de mutar."""
        with self._candado:
            id = registro["id"]
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo == registro:
                    return  # repetición idempotente
                raise ValueError(f"identificador ya usado con otros argumentos: {id!r}")

            origen = registro["origen"]
            destino = registro["destino"]
            cantidad = registro["cantidad"]

            if origen is not None and self._saldos.get(origen, 0) < cantidad:
                raise ValueError(f"saldo insuficiente en {origen!r}")

            # A partir de acá nada puede fallar.
            if origen is not None:
                self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
            if destino is not None:
                self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
            self._movimientos[id] = registro
            self._historial.append(registro)
            if registro["original"] is not None:
                self._revertidos.add(registro["original"])
