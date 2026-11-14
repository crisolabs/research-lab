"""Libro de inventario con movimientos idempotentes y reversibles."""

from __future__ import annotations

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


def _texto(valor: object, descripcion: str) -> str:
    """Devuelve ``valor`` como ``str`` exacto si es un string no vacío."""
    if isinstance(valor, str):
        # Copia exacta: una subclase de str no puede alterar hash ni igualdad.
        valor = str.__str__(valor)
        if valor:
            return valor
    raise ValueError(f"{descripcion} debe ser un string no vacío")


def _cantidad(valor: object) -> int:
    """Devuelve ``valor`` como ``int`` exacto si es entero positivo no booleano."""
    if isinstance(valor, int) and not isinstance(valor, bool):
        valor = int.__index__(valor)  # copia exacta, igual que en _texto
        if valor > 0:
            return valor
    raise ValueError("la cantidad debe ser un entero positivo y no booleano")


class Inventario:
    """Saldos por ubicación e historial ordenado de movimientos.

    Cada movimiento traslada ``cantidad`` unidades de ``origen`` a ``destino``;
    ``None`` representa el exterior del inventario (ingresos y retiros), de
    modo que revertir equivale a trasladar en sentido inverso.
    """

    def __init__(self) -> None:
        self._saldos = {}  # ubicación -> saldo; ausente equivale a cero
        self._historial = []  # registros en orden de aplicación
        self._movimientos = {}  # id -> registro
        self._firmas = {}  # id -> (operación, argumentos), para idempotencia
        self._revertidos = set()  # ids de movimientos ya revertidos

    def saldo(self, ubicacion: str) -> int:
        """Devuelve el saldo actual de ``ubicacion``."""
        return self._saldos.get(_texto(ubicacion, "la ubicación"), 0)

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Suma ``cantidad`` unidades a ``ubicacion``."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        firma = (_INGRESO, ubicacion, cantidad)
        if not self._repetido(id, firma):
            self._aplicar(id, firma, _INGRESO, None, ubicacion, cantidad)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Resta ``cantidad`` unidades de ``ubicacion`` si el saldo alcanza."""
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        firma = (_RETIRO, ubicacion, cantidad)
        if not self._repetido(id, firma):
            self._aplicar(id, firma, _RETIRO, ubicacion, None, cantidad)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        """Traslada ``cantidad`` unidades de ``origen`` a ``destino`` (todo o nada)."""
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        firma = (_TRANSFERENCIA, origen, destino, cantidad)
        if not self._repetido(id, firma):
            self._aplicar(id, firma, _TRANSFERENCIA, origen, destino, cantidad)

    def revertir(self, id: str, original: str) -> None:
        """Deshace, una única vez, el movimiento ``original``."""
        id = _texto(id, "el identificador")
        original = _texto(original, "el movimiento original")
        firma = (_REVERSION, original)
        if self._repetido(id, firma):
            return
        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError(f"no existe el movimiento {original!r}")
        if movimiento["tipo"] == _REVERSION:
            raise ValueError(f"{original!r} es una reversión y no puede revertirse")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        self._aplicar(
            id,
            firma,
            _REVERSION,
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def historial(self) -> list[dict]:
        """Devuelve una copia independiente de los movimientos aplicados."""
        return [dict(registro) for registro in self._historial]

    def _repetido(self, id: str, firma: tuple) -> bool:
        """Indica si ``id`` ya aplicó ``firma``; falla si lo usó con otra."""
        previa = self._firmas.get(id)
        if previa is None:
            return False
        if previa != firma:
            raise ValueError(
                f"el identificador {id!r} ya se usó con otra operación o argumentos"
            )
        return True

    def _aplicar(
        self, id, firma, tipo, origen, destino, cantidad, original=None
    ) -> None:
        """Valida los saldos resultantes y sólo entonces confirma el movimiento."""
        nuevos = {}
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: "
                    f"hay {disponible}, se requieren {cantidad}"
                )
            nuevos[origen] = disponible - cantidad
        if destino is not None:
            nuevos[destino] = self._saldos.get(destino, 0) + cantidad
        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        # Sin validaciones desde aquí: el cambio se confirma completo.
        self._saldos.update(nuevos)
        self._historial.append(registro)
        self._movimientos[id] = registro
        self._firmas[id] = firma
        if original is not None:
            self._revertidos.add(original)
