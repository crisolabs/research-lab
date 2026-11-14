import math
import reprlib
from collections.abc import Mapping, Set
from itertools import islice
from operator import itemgetter

# Iterables que no son un par ordenado (inicio, fin): texto y datos binarios
# (sus elementos son caracteres o bytes) y colecciones sin orden posicional.
_NO_SON_PARES = (str, bytes, bytearray, memoryview, Set, Mapping)


class _EntradaNoIterable(TypeError, ValueError):
    """unir() recibió algo que no es iterable.

    Es ValueError, como toda entrada inválida, y a la vez TypeError, que es
    lo que usa Python para objetos no iterables.
    """


def _mal_formado(indice, intervalo, motivo):
    return ValueError(
        f"intervalo mal formado en el índice {indice} "
        f"({reprlib.repr(intervalo)}): {motivo}"
    )


def _validar_extremo(valor, indice):
    """Lanza ValueError si valor no es un int o float finito (o es bool)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(
            f"extremo inválido en el índice {indice}: {reprlib.repr(valor)} "
            "(se esperaba un int o float que no sea bool)"
        )
    # Todo int es finito; además, math.isfinite lanzaría OverflowError con un
    # int demasiado grande para convertirse a float.
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(
            f"extremo no finito en el índice {indice}: {reprlib.repr(valor)}"
        )


def _validar_intervalo(intervalo, indice):
    """Devuelve la tupla (inicio, fin) del intervalo o lanza ValueError."""
    if isinstance(intervalo, (list, tuple)):
        extremos = intervalo  # Caso habitual: se mide y desempaqueta directo.
    elif isinstance(intervalo, _NO_SON_PARES):
        raise _mal_formado(indice, intervalo, "no es un par [inicio, fin]")
    else:
        try:
            iterador = iter(intervalo)
        except TypeError:
            raise _mal_formado(indice, intervalo, "no es iterable") from None
        # Leer tres elementos alcanza para detectar uno de más, sin consumir
        # de más (ni colgarse) con iteradores largos o infinitos.
        extremos = tuple(islice(iterador, 3))
    if len(extremos) != 2:
        raise _mal_formado(
            indice, intervalo, "debe tener exactamente dos extremos"
        )
    inicio, fin = extremos
    _validar_extremo(inicio, indice)
    _validar_extremo(fin, indice)
    if inicio > fin:
        raise _mal_formado(
            indice,
            intervalo,
            f"el inicio {reprlib.repr(inicio)} es mayor que el fin "
            f"{reprlib.repr(fin)}",
        )
    return inicio, fin


def unir(intervalos):
    """Une los intervalos cerrados que se superponen o se tocan.

    intervalos puede ser cualquier iterable; se recorre una sola vez y no se
    modifica. Cada intervalo debe tener exactamente dos extremos int o float
    finitos (no bool), con inicio <= fin. Devuelve una lista nueva de listas
    [inicio, fin] disjuntas, ordenadas por inicio.

    Lanza ValueError ante intervalos mal formados o extremos inválidos (si
    intervalos no es iterable, la excepción es además TypeError).
    """
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise _EntradaNoIterable(
            "se esperaba un iterable de intervalos, no "
            f"{type(intervalos).__name__}"
        ) from None

    pares = [
        _validar_intervalo(intervalo, indice)
        for indice, intervalo in enumerate(iterador)
    ]
    pares.sort(key=itemgetter(0))

    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            # Se superpone con el último intervalo unido o lo toca.
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
