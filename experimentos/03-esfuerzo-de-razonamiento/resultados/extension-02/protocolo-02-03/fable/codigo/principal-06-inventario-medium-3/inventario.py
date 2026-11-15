"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro (dict)
        self._historial = []
        self._revertidos = set()  # ids de movimientos ya revertidos
        self._lock = threading.RLock()

    # ------------------------------------------------------------ consultas

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        with self._lock:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._lock:
            return [dict(m) for m in self._historial]

    # ----------------------------------------------------------- mutaciones

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "ingreso", None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "retiro", ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar(
            self._registro(id, "transferencia", origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        with self._lock:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo["tipo"] == "reversion" and previo["original"] == original:
                    return None  # repetición idempotente
                raise ValueError(f"identificador ya usado: {id!r}")
            mov = self._movimientos.get(original)
            if mov is None:
                raise ValueError(f"movimiento inexistente: {original!r}")
            if mov["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"movimiento ya revertido: {original!r}")
            registro = self._registro(
                id, "reversion", mov["destino"], mov["origen"], mov["cantidad"],
                original,
            )
            self._aplicar(registro)
            self._revertidos.add(original)
        return None

    # -------------------------------------------------------------- interno

    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _aplicar(self, registro):
        """Aplica el registro: resta de `origen` y suma a `destino`."""
        with self._lock:
            previo = self._movimientos.get(registro["id"])
            if previo is not None:
                if previo == registro:
                    return  # repetición idempotente
                raise ValueError(f"identificador ya usado: {registro['id']!r}")
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
            self._movimientos[registro["id"]] = registro
            self._historial.append(registro)
