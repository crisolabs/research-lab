"""Implementá el libro de inventario pedido en TAREA.md."""

from typing import Any


def _validar_texto(valor: Any, nombre: str) -> None:
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(valor: Any) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo y no booleano")


class Inventario:
    def __init__(self) -> None:
        self._saldos: dict[str, int] = {}
        self._movimientos: dict[str, dict[str, Any]] = {}
        self._historial: list[dict[str, Any]] = []
        self._revertidos: set[str] = set()

    def saldo(self, ubicacion: str) -> int:
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "ingreso", None, ubicacion, cantidad, None)
        if self._ya_aplicado(registro):
            return
        self._mover(None, ubicacion, cantidad)
        self._guardar(registro)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "retiro", ubicacion, None, cantidad, None)
        if self._ya_aplicado(registro):
            return
        self._exigir_saldo(ubicacion, cantidad)
        self._mover(ubicacion, None, cantidad)
        self._guardar(registro)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "la ubicación de origen")
        _validar_texto(destino, "la ubicación de destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        registro = self._registro(id, "transferencia", origen, destino, cantidad, None)
        if self._ya_aplicado(registro):
            return
        self._exigir_saldo(origen, cantidad)
        self._mover(origen, destino, cantidad)
        self._guardar(registro)

    def revertir(self, id: str, original: str) -> None:
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        if id in self._movimientos:
            previo = self._movimientos[id]
            if previo["tipo"] == "reversion" and previo["original"] == original:
                return
            raise ValueError(f"el identificador {id!r} ya se usó con otros argumentos")
        if original not in self._movimientos:
            raise ValueError(f"movimiento original inexistente: {original!r}")
        mov = self._movimientos[original]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        # La reversión invierte origen y destino respecto del movimiento original.
        origen, destino, cantidad = mov["destino"], mov["origen"], mov["cantidad"]
        self._exigir_saldo(origen, cantidad)
        self._mover(origen, destino, cantidad)
        self._revertidos.add(original)
        self._guardar(
            self._registro(id, "reversion", origen, destino, cantidad, original)
        )

    def historial(self) -> list[dict[str, Any]]:
        return [dict(registro) for registro in self._historial]

    @staticmethod
    def _registro(
        id: str,
        tipo: str,
        origen: str | None,
        destino: str | None,
        cantidad: int,
        original: str | None,
    ) -> dict[str, Any]:
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _ya_aplicado(self, registro: dict[str, Any]) -> bool:
        previo = self._movimientos.get(registro["id"])
        if previo is None:
            return False
        if previo != registro:
            raise ValueError(
                f"el identificador {registro['id']!r} ya se usó con otros argumentos"
            )
        return True

    def _exigir_saldo(self, ubicacion: str | None, cantidad: int) -> None:
        if ubicacion is not None and self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError(f"saldo insuficiente en {ubicacion!r}")

    def _mover(self, origen: str | None, destino: str | None, cantidad: int) -> None:
        if origen is not None:
            self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad

    def _guardar(self, registro: dict[str, Any]) -> None:
        self._movimientos[registro["id"]] = registro
        self._historial.append(registro)
