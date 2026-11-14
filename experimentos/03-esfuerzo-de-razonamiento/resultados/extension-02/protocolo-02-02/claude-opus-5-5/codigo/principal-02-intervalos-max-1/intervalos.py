import math
from collections.abc import Mapping, Set


def _es_extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    # Los enteros siempre son finitos (y math.isfinite desborda con enteros enormes).
    return isinstance(valor, int) or math.isfinite(valor)


def _validar_intervalo(intervalo):
    # Cadenas, bytes, mapeos y conjuntos son iterables, pero no pares ordenados.
    if isinstance(intervalo, (str, bytes, bytearray, Mapping, Set)):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        inicio, fin = intervalo
    except (TypeError, ValueError):
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    for extremo in (inicio, fin):
        if not _es_extremo_valido(extremo):
            raise ValueError(f"extremo inválido: {extremo!r}")
    if inicio > fin:
        raise ValueError(f"el inicio es mayor que el fin: [{inicio!r}, {fin!r}]")
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    unidos = []
    for inicio, fin in sorted(_validar_intervalo(intervalo) for intervalo in iterador):
        # Con `<=` también se unen los intervalos cerrados que sólo se tocan.
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
