"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return str.__str__(valor)


def _validar_cantidad(cantidad):
    if (
        isinstance(cantidad, bool)
        or not isinstance(cantidad, int)
        or cantidad <= 0
    ):
        raise ValueError("la cantidad debe ser un entero positivo")
    return int(cantidad)


class Inventario:
    """Libro de inventario por ubicación."""

    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> firma (tipo y argumentos) del movimiento aplicado
        self._firmas = {}
        # id -> registro del movimiento en el historial
        self._registros = {}
        # ids de movimientos originales que ya fueron revertidos
        self._revertidos = set()
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def saldo(self, ubicacion):
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        with self._lock:
            return int(self._saldos.get(ubicacion, 0))

    def historial(self):
        with self._lock:
            return [dict(registro) for registro in self._historial]

    # ------------------------------------------------------------------
    # Mutaciones
    # ------------------------------------------------------------------
    def ingresar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "el identificador")
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        firma = (_INGRESO, ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id, firma, _INGRESO, None, ubicacion, cantidad, None
            )
        return None

    def retirar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "el identificador")
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        firma = (_RETIRO, ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id, firma, _RETIRO, ubicacion, None, cantidad, None
            )
        return None

    def transferir(self, id, origen, destino, cantidad):
        id = _validar_texto(id, "el identificador")
        origen = _validar_texto(origen, "el origen")
        destino = _validar_texto(destino, "el destino")
        cantidad = _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = (_TRANSFERENCIA, origen, destino, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._aplicar(
                id, firma, _TRANSFERENCIA, origen, destino, cantidad, None
            )
        return None

    def revertir(self, id, original):
        id = _validar_texto(id, "el identificador")
        original = _validar_texto(original, "el movimiento original")
        firma = (_REVERSION, original)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            registro = self._registros.get(original)
            if registro is None:
                raise ValueError(f"el movimiento {original!r} no existe")
            if registro["tipo"] == _REVERSION:
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(
                    f"el movimiento {original!r} ya fue revertido"
                )
            self._aplicar(
                id,
                firma,
                _REVERSION,
                registro["destino"],
                registro["origen"],
                registro["cantidad"],
                original,
            )
        return None

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _ya_aplicado(self, id, firma):
        """Indica si ``id`` ya se aplicó con ``firma``.

        Lanza ``ValueError`` si el identificador se usó con otra operación
        u otros argumentos.
        """
        existente = self._firmas.get(id)
        if existente is None:
            return False
        if existente == firma:
            return True
        raise ValueError(
            f"el identificador {id!r} ya se usó con otros argumentos"
        )

    def _aplicar(self, id, firma, tipo, origen, destino, cantidad, original):
        """Aplica el movimiento de forma atómica o lanza sin efectos."""
        nuevos = {}
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: "
                    f"{disponible} < {cantidad}"
                )
            nuevos[origen] = disponible - cantidad
        if destino is not None:
            nuevos[destino] = nuevos.get(
                destino, self._saldos.get(destino, 0)
            ) + cantidad
        if any(valor < 0 for valor in nuevos.values()):
            raise ValueError("ningún saldo puede quedar negativo")

        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

        # Commit: sólo operaciones que no fallan.
        self._saldos.update(nuevos)
        self._historial.append(registro)
        self._firmas[id] = firma
        self._registros[id] = registro
        if original is not None:
            self._revertidos.add(original)
