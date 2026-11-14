"""Libro de inventario con movimientos idempotentes, atómicos y reversibles."""

from __future__ import annotations

__all__ = ["Inventario"]

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


def _texto(valor: object, que: str) -> str:
    """Devuelve ``valor`` como ``str`` exacto si es un string no vacío; si no, ``ValueError``."""
    # Se mira type() y no isinstance() para rechazar objetos que sólo simulan ser
    # str mediante __class__ (p. ej. mocks); str.__str__ obtiene una copia ``str``
    # exacta sin ejecutar métodos que una subclase pudiera redefinir.
    if issubclass(type(valor), str):
        texto = str.__str__(valor)
        if texto:
            return texto
    raise ValueError(f"{que} debe ser un string no vacío")


def _cantidad(valor: object) -> int:
    """Devuelve ``valor`` como ``int`` exacto si es un entero positivo no booleano; si no, ``ValueError``."""
    tipo = type(valor)
    if issubclass(tipo, int) and not issubclass(tipo, bool):
        numero = int.__int__(valor)
        if numero > 0:
            return numero
    raise ValueError("la cantidad debe ser un entero positivo y no booleano")


def _registro(id, tipo, origen, destino, cantidad, original=None) -> dict:
    return {
        "id": id,
        "tipo": tipo,
        "origen": origen,
        "destino": destino,
        "cantidad": cantidad,
        "original": original,
    }


def _firma(registro: dict) -> tuple:
    """Operación y argumentos de la llamada que originó ``registro``."""
    if registro["tipo"] == _REVERSION:
        return (_REVERSION, registro["original"])
    return (registro["tipo"], registro["origen"], registro["destino"], registro["cantidad"])


class Inventario:
    """Saldos por ubicación (inicialmente cero) e historial de movimientos.

    Cada movimiento lleva un identificador único: repetir una llamada idéntica no
    tiene efecto y reusar el identificador con otros argumentos lanza ``ValueError``.
    Ante cualquier excepción el libro queda exactamente como estaba.
    """

    def __init__(self) -> None:
        self._saldos: dict[str, int] = {}  # ubicación -> saldo; ausente equivale a 0
        self._historial: list[dict] = []  # registros en orden de aplicación
        self._movimientos: dict[str, dict] = {}  # id -> registro
        self._revertido_por: dict[str, str] = {}  # id revertido -> id de su reversión

    # Consultas

    def saldo(self, ubicacion: str) -> int:
        """Saldo actual de ``ubicacion``."""
        return self._saldos.get(_texto(ubicacion, "la ubicación"), 0)

    def historial(self) -> list[dict]:
        """Copia de los movimientos aplicados, en orden de aplicación."""
        return [dict(registro) for registro in self._historial]

    # Movimientos

    def ingresar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Suma ``cantidad`` unidades a ``ubicacion``."""
        self._registrar(
            _texto(id, "el identificador"),
            _INGRESO,
            None,
            _texto(ubicacion, "la ubicación"),
            _cantidad(cantidad),
        )

    def retirar(self, id: str, ubicacion: str, cantidad: int) -> None:
        """Resta ``cantidad`` unidades de ``ubicacion``; ``ValueError`` si no alcanzan."""
        self._registrar(
            _texto(id, "el identificador"),
            _RETIRO,
            _texto(ubicacion, "la ubicación"),
            None,
            _cantidad(cantidad),
        )

    def transferir(self, id: str, origen: str, destino: str, cantidad: int) -> None:
        """Mueve ``cantidad`` unidades de ``origen`` a ``destino`` de forma atómica."""
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        self._registrar(id, _TRANSFERENCIA, origen, destino, cantidad)

    def revertir(self, id: str, original: str) -> None:
        """Deshace, una única vez, el ingreso, retiro o transferencia ``original``."""
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador original")
        if self._ya_aplicado(id, (_REVERSION, original)):
            return
        movimiento = self._movimientos.get(original)
        if movimiento is None:
            raise ValueError(f"no existe el movimiento {original!r}")
        if movimiento["tipo"] == _REVERSION:
            raise ValueError(f"{original!r} es una reversión y no puede revertirse")
        if original in self._revertido_por:
            raise ValueError(
                f"el movimiento {original!r} ya fue revertido por "
                f"{self._revertido_por[original]!r}"
            )
        # Con origen y destino intercambiados, aplicar la reversión deshace el original.
        self._aplicar(
            _registro(
                id,
                _REVERSION,
                movimiento["destino"],
                movimiento["origen"],
                movimiento["cantidad"],
                original,
            )
        )

    # Internos

    def _registrar(self, id, tipo, origen, destino, cantidad) -> None:
        """Aplica un movimiento que no es reversión, con argumentos ya validados."""
        registro = _registro(id, tipo, origen, destino, cantidad)
        if not self._ya_aplicado(id, _firma(registro)):
            self._aplicar(registro)

    def _ya_aplicado(self, id: str, firma: tuple) -> bool:
        """``True`` si ``id`` ya se aplicó con la misma operación y argumentos.

        Lanza ``ValueError`` si ``id`` ya se usó con otra operación u otros argumentos.
        """
        existente = self._movimientos.get(id)
        if existente is None:
            return False
        if _firma(existente) != firma:
            raise ValueError(
                f"el identificador {id!r} ya se usó con otra operación o argumentos"
            )
        return True

    def _aplicar(self, registro: dict) -> None:
        """Aplica un movimiento nuevo: valida los saldos resultantes y confirma todo o nada.

        Resta ``cantidad`` del origen y la suma al destino (si no son ``None``;
        nunca son iguales), así que vale tanto para movimientos como para reversiones.
        """
        cantidad = registro["cantidad"]
        origen, destino = registro["origen"], registro["destino"]
        nuevos = {}
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: hay {disponible} "
                    f"y se necesitan {cantidad}"
                )
            nuevos[origen] = disponible - cantidad
        if destino is not None:
            nuevos[destino] = self._saldos.get(destino, 0) + cantidad

        # Hasta acá no se modificó nada. Se confirma; si algo fallara a mitad de
        # camino (p. ej. MemoryError), se restaura el estado previo completo.
        anteriores = {ubicacion: self._saldos.get(ubicacion) for ubicacion in nuevos}
        id, original = registro["id"], registro["original"]
        try:
            self._movimientos[id] = registro
            self._historial.append(registro)
            if original is not None:
                self._revertido_por[original] = id
            self._saldos.update(nuevos)
        except BaseException:
            self._movimientos.pop(id, None)
            if self._historial and self._historial[-1] is registro:
                self._historial.pop()
            if original is not None:
                self._revertido_por.pop(original, None)
            for ubicacion, previo in anteriores.items():
                if previo is None:
                    self._saldos.pop(ubicacion, None)
                else:
                    self._saldos[ubicacion] = previo
            raise
