"""Implementá el libro de inventario pedido en TAREA.md."""

from typing import Any


class Inventario:
    """Libro de inventario con movimientos idempotentes y reversibles."""

    def __init__(self) -> None:
        self._saldos: dict[str, int] = {}
        self._movimientos: dict[str, dict[str, Any]] = {}
        self._historial: list[dict[str, Any]] = []
        self._revertidos: set[str] = set()

    # Consultas

    def saldo(self, ubicacion: str) -> int:
        """Devuelve el saldo de una ubicación (cero si nunca tuvo movimientos)."""
        ubicacion = _texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def historial(self) -> list[dict[str, Any]]:
        """Devuelve una copia del historial en orden de aplicación."""
        return [dict(mov) for mov in self._historial]

    # Mutaciones

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Suma unidades a una ubicación."""
        mov = {
            "id": _texto(id, "identificador"),
            "tipo": "ingreso",
            "origen": None,
            "destino": _texto(ubicacion, "ubicación"),
            "cantidad": _cantidad(cantidad),
            "original": None,
        }
        if self._ya_registrado(mov):
            return
        self._aplicar(mov)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Resta unidades de una ubicación; exige saldo suficiente."""
        mov = {
            "id": _texto(id, "identificador"),
            "tipo": "retiro",
            "origen": _texto(ubicacion, "ubicación"),
            "destino": None,
            "cantidad": _cantidad(cantidad),
            "original": None,
        }
        if self._ya_registrado(mov):
            return
        if self.saldo(mov["origen"]) < mov["cantidad"]:
            raise ValueError(f"saldo insuficiente en {mov['origen']!r}")
        self._aplicar(mov)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        """Mueve unidades de origen a destino de forma atómica."""
        mov = {
            "id": _texto(id, "identificador"),
            "tipo": "transferencia",
            "origen": _texto(origen, "ubicación"),
            "destino": _texto(destino, "ubicación"),
            "cantidad": _cantidad(cantidad),
            "original": None,
        }
        if mov["origen"] == mov["destino"]:
            raise ValueError("origen y destino deben ser distintos")
        if self._ya_registrado(mov):
            return
        if self.saldo(mov["origen"]) < mov["cantidad"]:
            raise ValueError(f"saldo insuficiente en {mov['origen']!r}")
        self._aplicar(mov)

    def revertir(self, id: str, original: str) -> None:
        """Revierte exactamente una vez un ingreso, retiro o transferencia."""
        rev_id = _texto(id, "identificador")
        orig_id = _texto(original, "identificador")

        previo = self._movimientos.get(rev_id)
        if previo is not None:
            if previo["tipo"] == "reversion" and previo["original"] == orig_id:
                return  # Repetición idéntica: no cambia nada.
            raise ValueError(f"el identificador {rev_id!r} ya se usó con otros argumentos")

        orig = self._movimientos.get(orig_id)
        if orig is None:
            raise ValueError(f"movimiento original inexistente: {orig_id!r}")
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if orig_id in self._revertidos:
            raise ValueError(f"el movimiento {orig_id!r} ya fue revertido")

        # La reversión deshace los efectos: intercambia origen y destino.
        mov = {
            "id": rev_id,
            "tipo": "reversion",
            "origen": orig["destino"],
            "destino": orig["origen"],
            "cantidad": orig["cantidad"],
            "original": orig_id,
        }
        # Sólo el origen de la reversión pierde unidades: validar que no quede negativo.
        if mov["origen"] is not None and self.saldo(mov["origen"]) < mov["cantidad"]:
            raise ValueError(f"la reversión dejaría negativo el saldo de {mov['origen']!r}")
        self._aplicar(mov)

    # Auxiliares

    def _ya_registrado(self, mov: dict[str, Any]) -> bool:
        """True si el identificador ya existe con exactamente la misma operación.

        Lanza ValueError si el identificador existe con argumentos distintos.
        """
        previo = self._movimientos.get(mov["id"])
        if previo is None:
            return False
        if previo == mov:
            return True
        raise ValueError(f"el identificador {mov['id']!r} ya se usó con otros argumentos")

    def _aplicar(self, mov: dict[str, Any]) -> None:
        """Aplica un movimiento ya validado y lo registra. No puede fallar."""
        cantidad = mov["cantidad"]
        if mov["origen"] is not None:
            self._saldos[mov["origen"]] = self._saldos.get(mov["origen"], 0) - cantidad
        if mov["destino"] is not None:
            self._saldos[mov["destino"]] = self._saldos.get(mov["destino"], 0) + cantidad
        self._movimientos[mov["id"]] = mov
        self._historial.append(mov)
        if mov["tipo"] == "reversion":
            self._revertidos.add(mov["original"])


def _texto(valor: object, nombre: str) -> str:
    """Valida un string no vacío (ubicaciones e identificadores)."""
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor: object) -> int:
    """Valida un entero positivo que no sea booleano."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor
