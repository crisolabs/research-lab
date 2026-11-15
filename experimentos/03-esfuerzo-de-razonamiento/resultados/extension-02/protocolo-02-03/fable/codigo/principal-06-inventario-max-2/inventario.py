"""Libro de inventario en memoria con movimientos idempotentes y reversibles.

Cada movimiento lleva un identificador elegido por quien llama: repetirlo con la
misma operación y los mismos argumentos no hace nada, y reutilizarlo para otra
cosa es un error. Todo error de uso se informa con ``ValueError`` y deja el libro
exactamente como estaba.
"""

import threading
from typing import Any, Dict, List, NamedTuple, Optional

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


class _TipoInvalido(ValueError, TypeError):
    """Argumento de un tipo no admitido.

    Es el ``ValueError`` que pide el contrato y, para quien atrapa errores de
    tipo, también un ``TypeError``.
    """


class _Movimiento(NamedTuple):
    """Asiento inmutable: `cantidad` unidades salen de `origen` y entran en `destino`.

    Un extremo en ``None`` es el exterior del inventario. Una reversión lleva los
    extremos de su original intercambiados, así que se aplica igual que cualquier
    otro movimiento.
    """

    id: str
    tipo: str
    origen: Optional[str]
    destino: Optional[str]
    cantidad: int
    original: Optional[str]


def _texto(valor: Any, nombre: str) -> str:
    """Valida que `valor` sea un string no vacío y lo devuelve como ``str`` exacto."""
    if not isinstance(valor, str):
        raise _TipoInvalido(
            f"{nombre} debe ser un string no vacío, no {type(valor).__name__}"
        )
    # Copia exacta del contenido: al libro no entran subclases de str, que
    # podrían redefinir la comparación o el hash, o ser mutables.
    valor = str.__str__(valor)
    if not valor:
        raise ValueError(f"{nombre} no puede ser un string vacío")
    return valor


def _cantidad(valor: Any) -> int:
    """Valida que `valor` sea un entero positivo no booleano y lo devuelve como ``int`` exacto."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _TipoInvalido(
            f"cantidad debe ser un entero positivo, no {type(valor).__name__}"
        )
    valor = int.__index__(valor)  # ídem: al libro no entran subclases de int
    if valor <= 0:
        raise ValueError("cantidad debe ser un entero positivo")
    return valor


class Inventario:
    """Saldos por ubicación, modificados sólo mediante movimientos identificados.

    Cada operación valida sus argumentos, después las reglas del libro y recién
    entonces escribe, de modo que una excepción nunca deja cambios a medias ni
    consume el identificador. Un candado serializa las operaciones para que eso
    valga también cuando varios hilos comparten el libro.
    """

    def __init__(self) -> None:
        self._candado = threading.RLock()
        self._saldos: Dict[str, int] = {}  # las ubicaciones ausentes valen cero
        self._movimientos: Dict[str, _Movimiento] = {}  # en orden de aplicación
        self._reversiones: Dict[str, str] = {}  # id revertido -> id de su reversión

    def saldo(self, ubicacion: str) -> int:
        """Devuelve las unidades que hay en `ubicacion` (cero si nunca se usó)."""
        ubicacion = _texto(ubicacion, "ubicacion")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Suma `cantidad` unidades a `ubicacion`."""
        movimiento = _Movimiento(
            id=_texto(id, "id"),
            tipo=_INGRESO,
            origen=None,
            destino=_texto(ubicacion, "ubicacion"),
            cantidad=_cantidad(cantidad),
            original=None,
        )
        with self._candado:
            self._asentar(movimiento)

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Resta `cantidad` unidades de `ubicacion`; falla si el saldo no alcanza."""
        movimiento = _Movimiento(
            id=_texto(id, "id"),
            tipo=_RETIRO,
            origen=_texto(ubicacion, "ubicacion"),
            destino=None,
            cantidad=_cantidad(cantidad),
            original=None,
        )
        with self._candado:
            self._asentar(movimiento)

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        """Pasa `cantidad` unidades de `origen` a `destino`: ocurre todo o nada."""
        movimiento = _Movimiento(
            id=_texto(id, "id"),
            tipo=_TRANSFERENCIA,
            origen=_texto(origen, "origen"),
            destino=_texto(destino, "destino"),
            cantidad=_cantidad(cantidad),
            original=None,
        )
        if movimiento.origen == movimiento.destino:
            raise ValueError(
                f"origen y destino deben ser distintos, no {movimiento.origen!r} ambos"
            )
        with self._candado:
            self._asentar(movimiento)

    def revertir(self, id: str, original: str) -> None:
        """Deshace, una única vez, el ingreso, retiro o transferencia `original`."""
        id = _texto(id, "id")
        original = _texto(original, "original")
        with self._candado:
            base = self._movimientos.get(original)
            if base is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if base.tipo == _REVERSION:
                raise ValueError(
                    f"{original!r} es una reversión y no se puede revertir"
                )
            self._asentar(
                _Movimiento(
                    id=id,
                    tipo=_REVERSION,
                    origen=base.destino,
                    destino=base.origen,
                    cantidad=base.cantidad,
                    original=original,
                )
            )

    def historial(self) -> List[Dict[str, Any]]:
        """Devuelve los movimientos aplicados, en orden, como diccionarios nuevos.

        La lista y sus diccionarios son copias: modificarlos no altera el libro.
        """
        with self._candado:
            movimientos = list(self._movimientos.values())
        return [movimiento._asdict() for movimiento in movimientos]

    def _asentar(self, movimiento: _Movimiento) -> None:
        """Aplica `movimiento`, o no hace nada si ya está asentado tal cual.

        Requiere el candado tomado. Todas las comprobaciones preceden a la primera
        escritura: si lanza ``ValueError``, el libro no cambió.
        """
        previo = self._movimientos.get(movimiento.id)
        if previo is not None:
            # La repetición exacta se reconoce antes de mirar saldos o marcas de
            # reversión: es idempotente aunque hoy ya no pudiera aplicarse.
            if previo == movimiento:
                return
            raise ValueError(
                f"el identificador {movimiento.id!r} ya se usó con otra operación"
                " o con otros argumentos"
            )

        revertido_por = self._reversiones.get(movimiento.original)
        if revertido_por is not None:
            raise ValueError(
                f"el movimiento {movimiento.original!r} ya fue revertido"
                f" por {revertido_por!r}"
            )

        saldos = {}
        if movimiento.origen is not None:
            disponible = self._saldos.get(movimiento.origen, 0)
            if disponible < movimiento.cantidad:
                raise ValueError(
                    f"saldo insuficiente en {movimiento.origen!r}: hay {disponible}"
                    f" y se necesitan {movimiento.cantidad}"
                )
            saldos[movimiento.origen] = disponible - movimiento.cantidad
        if movimiento.destino is not None:
            saldos[movimiento.destino] = (
                self._saldos.get(movimiento.destino, 0) + movimiento.cantidad
            )

        self._saldos.update(saldos)
        self._movimientos[movimiento.id] = movimiento
        if movimiento.original is not None:
            self._reversiones[movimiento.original] = movimiento.id

    def __getstate__(self) -> Dict[str, Any]:
        # El candado no se puede copiar ni serializar: viaja sólo el contenido
        # del libro, y cada copia estrena su propio candado en __setstate__.
        with self._candado:
            return {
                "_saldos": dict(self._saldos),
                "_movimientos": dict(self._movimientos),
                "_reversiones": dict(self._reversiones),
            }

    def __setstate__(self, estado: Dict[str, Any]) -> None:
        self.__dict__.update(estado)
        self._candado = threading.RLock()
