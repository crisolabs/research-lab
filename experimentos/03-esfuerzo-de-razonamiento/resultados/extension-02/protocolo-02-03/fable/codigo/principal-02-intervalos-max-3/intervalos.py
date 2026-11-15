import math
from collections.abc import Mapping, Set

__all__ = ["unir"]

# Iterables que no son intervalos aunque produzcan dos enteros: las cadenas
# (de texto o binarias) y las colecciones sin un orden «inicio, fin» definido.
_NO_SON_INTERVALOS = (str, bytes, bytearray, Set, Mapping)


def _es_extremo(valor):
    """Indica si `valor` es un entero o un flotante finito (nunca un booleano)."""
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    return isinstance(valor, float) and math.isfinite(valor)


def _extremos(intervalo, posicion):
    """Devuelve `(inicio, fin)` o lanza `ValueError` si el intervalo es inválido."""
    if isinstance(intervalo, _NO_SON_INTERVALOS):
        raise ValueError(
            f"intervalo en la posición {posicion}: "
            f"un {type(intervalo).__name__} no es un intervalo"
        )
    try:
        inicio, fin = intervalo
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"intervalo en la posición {posicion}: "
            "debe contener exactamente dos extremos"
        ) from error
    for extremo in (inicio, fin):
        if not _es_extremo(extremo):
            raise ValueError(
                f"intervalo en la posición {posicion}: extremo inválido de tipo "
                f"{type(extremo).__name__}; se esperaba un entero o un flotante finito"
            )
    if inicio > fin:
        raise ValueError(
            f"intervalo en la posición {posicion}: el inicio es mayor que el fin"
        )
    return inicio, fin


def unir(intervalos):
    """Une intervalos cerrados superpuestos o que se tocan.

    Devuelve una lista nueva de listas `[inicio, fin]` ordenadas, sin modificar
    la entrada; lanza `ValueError` si la entrada o algún intervalo es inválido.
    """
    try:
        iterador = iter(intervalos)
    except TypeError as error:
        raise ValueError("la entrada debe ser un iterable de intervalos") from error

    pares = sorted(
        _extremos(intervalo, posicion) for posicion, intervalo in enumerate(iterador)
    )

    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            # `max` conserva el fin ya acumulado cuando ambos son iguales.
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
