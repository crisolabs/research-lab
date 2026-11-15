import math
from collections.abc import Mapping, Set
from itertools import islice

_NO_INTERVALOS = (str, bytes, bytearray, memoryview, Mapping, Set)


def _extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    # Los enteros siempre son finitos; math.isfinite desbordaría con enteros enormes.
    return not isinstance(valor, float) or math.isfinite(valor)


def _normalizar(par):
    # Textos, bytes, mapeos y conjuntos no representan un par ordenado de extremos.
    if isinstance(par, _NO_INTERVALOS):
        raise ValueError(f"intervalo mal formado: {par!r}")
    try:
        iterador = iter(par)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {par!r}") from None
    # Se leen como mucho tres elementos para no colgarse con iteradores infinitos.
    extremos = list(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(
            f"un intervalo debe tener exactamente dos extremos: {par!r}"
        )
    inicio, fin = extremos
    if not _extremo_valido(inicio) or not _extremo_valido(fin):
        raise ValueError(
            f"los extremos deben ser enteros o flotantes finitos: {extremos!r}"
        )
    if inicio > fin:
        raise ValueError(f"el inicio no puede ser mayor que el fin: {extremos!r}")
    return [inicio, fin]


def unir(intervalos):
    if isinstance(intervalos, (str, bytes, bytearray, memoryview)):
        raise ValueError("la entrada debe ser un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    # Se valida todo y se trabaja sobre copias: la entrada no se modifica.
    pares = [_normalizar(par) for par in iterador]
    pares.sort(key=lambda par: (par[0], par[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
