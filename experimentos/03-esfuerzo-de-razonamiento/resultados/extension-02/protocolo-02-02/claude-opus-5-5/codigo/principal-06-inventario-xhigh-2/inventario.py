"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

__all__ = ["Inventario"]


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or len(valor) == 0:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    # Normaliza subclases de str a str exacto.
    return valor if type(valor) is str else str.__str__(valor)


def _validar_cantidad(cantidad):
    if (
        isinstance(cantidad, bool)
        or not isinstance(cantidad, int)
        or cantidad <= 0
    ):
        raise ValueError("la cantidad debe ser un entero positivo")
    return cantidad if type(cantidad) is int else int.__int__(cantidad)


class Inventario:
    """Libro de inventario por ubicación."""

    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> (firma, registro)
        self._movimientos = {}
        # id del movimiento original -> id de la reversión que lo revirtió
        self._revertidos = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def saldo(self, ubicacion):
        ubicacion = _validar_texto(ubicacion, "ubicacion")
        with self._lock:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._lock:
            return [dict(registro) for registro in self._historial]

    # ------------------------------------------------------------------ #
    # Mutaciones
    # ------------------------------------------------------------------ #
    def ingresar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "id")
        ubicacion = _validar_texto(ubicacion, "ubicacion")
        cantidad = _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id,
                firma,
                {
                    "id": id,
                    "tipo": "ingreso",
                    "origen": None,
                    "destino": ubicacion,
                    "cantidad": cantidad,
                    "original": None,
                },
                {ubicacion: cantidad},
            )
        return None

    def retirar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "id")
        ubicacion = _validar_texto(ubicacion, "ubicacion")
        cantidad = _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id,
                firma,
                {
                    "id": id,
                    "tipo": "retiro",
                    "origen": ubicacion,
                    "destino": None,
                    "cantidad": cantidad,
                    "original": None,
                },
                {ubicacion: -cantidad},
            )
        return None

    def transferir(self, id, origen, destino, cantidad):
        id = _validar_texto(id, "id")
        origen = _validar_texto(origen, "origen")
        destino = _validar_texto(destino, "destino")
        cantidad = _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id,
                firma,
                {
                    "id": id,
                    "tipo": "transferencia",
                    "origen": origen,
                    "destino": destino,
                    "cantidad": cantidad,
                    "original": None,
                },
                {origen: -cantidad, destino: cantidad},
            )
        return None

    def revertir(self, id, original):
        id = _validar_texto(id, "id")
        original = _validar_texto(original, "original")
        firma = ("reversion", original)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            entrada = self._movimientos.get(original)
            if entrada is None:
                raise ValueError(f"el movimiento original {original!r} no existe")
            registro_original = entrada[1]
            if registro_original["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")

            cantidad = registro_original["cantidad"]
            origen = registro_original["destino"]
            destino = registro_original["origen"]
            variaciones = {}
            if origen is not None:
                variaciones[origen] = variaciones.get(origen, 0) - cantidad
            if destino is not None:
                variaciones[destino] = variaciones.get(destino, 0) + cantidad

            self._aplicar(
                id,
                firma,
                {
                    "id": id,
                    "tipo": "reversion",
                    "origen": origen,
                    "destino": destino,
                    "cantidad": cantidad,
                    "original": original,
                },
                variaciones,
            )
            self._revertidos[original] = id
        return None

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #
    def _ya_aplicado(self, id, firma):
        """True si `id` ya se aplicó con la misma firma; error si difiere."""
        entrada = self._movimientos.get(id)
        if entrada is None:
            return False
        if entrada[0] != firma:
            raise ValueError(
                f"el identificador {id!r} ya se usó con otros argumentos"
            )
        return True

    def _aplicar(self, id, firma, registro, variaciones):
        """Aplica las variaciones atómicamente o lanza sin efectos."""
        nuevos = {}
        for ubicacion, delta in variaciones.items():
            nuevo = self._saldos.get(ubicacion, 0) + delta
            if nuevo < 0:
                raise ValueError(
                    f"saldo insuficiente en {ubicacion!r}"
                )
            nuevos[ubicacion] = nuevo
        # A partir de aquí no hay operaciones que puedan fallar.
        self._saldos.update(nuevos)
        self._movimientos[id] = (firma, registro)
        self._historial.append(registro)
