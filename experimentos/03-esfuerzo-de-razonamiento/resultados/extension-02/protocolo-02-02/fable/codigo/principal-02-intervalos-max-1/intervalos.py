import math
from collections.abc import Mapping, Set
from itertools import islice

__all__ = ["unir"]

# Iterables que nunca son un par ordenado de números: el texto y los bytes se
# recorren como caracteres u octetos, y los conjuntos y mapeos no definen de
# forma fiable cuál de sus elementos es el inicio y cuál el fin.
_NO_SON_PARES = (str, bytes, bytearray, memoryview, Set, Mapping)


def _error(posicion, detalle):
    return ValueError(f"intervalo en la posición {posicion}: {detalle}")


def _leer_par(intervalo, posicion):
    elementos = ()
    if not isinstance(intervalo, _NO_SON_PARES):
        try:
            # Con tres elementos alcanza para saber si son exactamente dos,
            # sin agotar un iterable largo o infinito.
            elementos = islice(intervalo, 3)
        except TypeError:  # No es iterable.
            pass
    extremos = tuple(elementos)
    if len(extremos) != 2:
        raise _error(posicion, "se esperaba un par [inicio, fin]")

    for extremo in extremos:
        # bool es subclase de int, así que se descarta de forma explícita.
        if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
            raise _error(
                posicion,
                f"extremo de tipo {type(extremo).__name__}; "
                "se esperaba un entero o un flotante",
            )
        # Los enteros siempre son finitos (y math.isfinite falla con los que
        # no caben en un float), así que sólo se revisan los flotantes.
        if isinstance(extremo, float) and not math.isfinite(extremo):
            raise _error(posicion, f"extremo no finito ({extremo!r})")

    if extremos[0] > extremos[1]:
        raise _error(posicion, "el inicio es mayor que el fin")
    return extremos


def unir(intervalos):
    try:
        numerados = enumerate(intervalos)
    except TypeError:
        raise ValueError(
            "la entrada debe ser un iterable de intervalos, no "
            f"{type(intervalos).__name__}"
        ) from None

    # Se valida y se copia todo en una única pasada: la entrada puede ser un
    # iterador de un solo uso y no debe modificarse.
    pares = sorted(
        _leer_par(intervalo, posicion) for posicion, intervalo in numerados
    )

    unidos = []
    for inicio, fin in pares:
        # Los intervalos son cerrados: basta compartir un extremo para unirse.
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
