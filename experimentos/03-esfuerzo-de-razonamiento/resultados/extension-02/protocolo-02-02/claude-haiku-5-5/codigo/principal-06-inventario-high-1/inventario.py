"""Implementá el libro de inventario pedido en TAREA.md."""

from typing import Any


def _texto(valor: Any, nombre: str) -> str:
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor: Any) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


class Inventario:
    def __init__(self) -> None:
        self._saldos: dict[str, int] = {}
        self._movimientos: list[dict[str, Any]] = []
        self._por_id: dict[str, dict[str, Any]] = {}
        self._revertidos: set[str] = set()

    def saldo(self, ubicacion: str) -> int:
        _texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        ubicacion = _texto(ubicacion, "la ubicación")
        mov = self._nuevo(id, "ingreso", None, ubicacion, _cantidad(cantidad), None)
        self._aplicar(mov)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        ubicacion = _texto(ubicacion, "la ubicación")
        mov = self._nuevo(id, "retiro", ubicacion, None, _cantidad(cantidad), None)
        self._aplicar(mov)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        origen = _texto(origen, "la ubicación de origen")
        destino = _texto(destino, "la ubicación de destino")
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        mov = self._nuevo(id, "transferencia", origen, destino, _cantidad(cantidad), None)
        self._aplicar(mov)

    def revertir(self, id: str, original: str) -> None:
        original = _texto(original, "el identificador de movimiento")
        previo = self._por_id.get(original)
        if previo is None:
            raise ValueError(f"movimiento original inexistente: {original!r}")
        if previo["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        mov = self._nuevo(
            id, "reversion", previo["destino"], previo["origen"], previo["cantidad"], original
        )
        self._aplicar(mov)

    def historial(self) -> list[dict[str, Any]]:
        return [dict(mov) for mov in self._movimientos]

    @staticmethod
    def _nuevo(
        id: Any,
        tipo: str,
        origen: str | None,
        destino: str | None,
        cantidad: int,
        original: str | None,
    ) -> dict[str, Any]:
        return {
            "id": _texto(id, "el identificador de movimiento"),
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _aplicar(self, mov: dict[str, Any]) -> None:
        previo = self._por_id.get(mov["id"])
        if previo is not None:
            if previo == mov:
                return
            raise ValueError(
                f"el identificador {mov['id']!r} ya se usó con otros argumentos"
            )
        if mov["tipo"] == "reversion" and mov["original"] in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = mov["cantidad"]
        origen = mov["origen"]
        destino = mov["destino"]
        if origen is not None and self.saldo(origen) < cantidad:
            raise ValueError(f"saldo insuficiente en {origen!r}")

        if origen is not None:
            self._saldos[origen] = self.saldo(origen) - cantidad
        if destino is not None:
            self._saldos[destino] = self.saldo(destino) + cantidad

        self._movimientos.append(mov)
        self._por_id[mov["id"]] = mov
        if mov["tipo"] == "reversion":
            self._revertidos.add(mov["original"])
