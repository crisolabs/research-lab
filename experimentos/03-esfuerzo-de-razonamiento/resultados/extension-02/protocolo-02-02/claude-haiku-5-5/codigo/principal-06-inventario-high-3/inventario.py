"""Implementá el libro de inventario pedido en TAREA.md."""

from typing import Any

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


def _validar_texto(valor: Any, nombre: str) -> str:
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _validar_cantidad(valor: Any) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


def _efectos(registro: dict[str, Any]) -> dict[str, int]:
    """Variación de saldo por ubicación que produce un movimiento."""
    efectos: dict[str, int] = {}
    cantidad = registro["cantidad"]
    if registro["origen"] is not None:
        efectos[registro["origen"]] = -cantidad
    if registro["destino"] is not None:
        efectos[registro["destino"]] = efectos.get(registro["destino"], 0) + cantidad
    return efectos


class Inventario:
    def __init__(self) -> None:
        self._saldos: dict[str, int] = {}
        self._historial: list[dict[str, Any]] = []
        self._por_id: dict[str, dict[str, Any]] = {}
        self._revertidos: set[str] = set()

    def saldo(self, ubicacion: str) -> int:
        _validar_texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        _validar_texto(id, "identificador")
        _validar_texto(ubicacion, "ubicación")
        _validar_cantidad(cantidad)
        registro = {
            "id": id,
            "tipo": _INGRESO,
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, registro)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        _validar_texto(id, "identificador")
        _validar_texto(ubicacion, "ubicación")
        _validar_cantidad(cantidad)
        registro = {
            "id": id,
            "tipo": _RETIRO,
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, registro)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        _validar_texto(id, "identificador")
        _validar_texto(origen, "origen")
        _validar_texto(destino, "destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        registro = {
            "id": id,
            "tipo": _TRANSFERENCIA,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        self._aplicar(id, registro)

    def revertir(self, id: str, original: str) -> None:
        _validar_texto(id, "identificador")
        _validar_texto(original, "original")

        existente = self._por_id.get(id)
        if existente is not None:
            if existente["tipo"] == _REVERSION and existente["original"] == original:
                return None
            raise ValueError(f"identificador {id!r} ya usado con otros argumentos")

        mov = self._por_id.get(original)
        if mov is None:
            raise ValueError(f"movimiento original {original!r} inexistente")
        if mov["tipo"] == _REVERSION:
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")

        registro = {
            "id": id,
            "tipo": _REVERSION,
            "origen": mov["destino"],
            "destino": mov["origen"],
            "cantidad": mov["cantidad"],
            "original": original,
        }
        self._aplicar(id, registro)
        self._revertidos.add(original)
        return None

    def historial(self) -> list[dict[str, Any]]:
        return [dict(registro) for registro in self._historial]

    def _aplicar(self, id: str, registro: dict[str, Any]) -> None:
        """Valida y aplica un movimiento de forma atómica.

        Si el identificador ya existe con exactamente el mismo movimiento,
        no hace nada. Cualquier error se lanza antes de modificar el estado.
        """
        existente = self._por_id.get(id)
        if existente is not None:
            if existente == registro:
                return None
            raise ValueError(f"identificador {id!r} ya usado con otros argumentos")

        efectos = _efectos(registro)
        for ubicacion, delta in efectos.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")

        for ubicacion, delta in efectos.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta
        self._por_id[id] = registro
        self._historial.append(registro)
        return None
