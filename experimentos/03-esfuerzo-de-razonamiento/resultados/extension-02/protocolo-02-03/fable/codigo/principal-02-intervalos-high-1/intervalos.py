import math
from collections.abc import Mapping, Set
from itertools import islice

_NO_SON_INTERVALOS = (str, bytes, bytearray, memoryview, Mapping, Set)


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar_intervalo(intervalo):
    if isinstance(intervalo, _NO_SON_INTERVALOS):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        iterador = iter(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    # Se leen a lo sumo tres elementos: alcanza para detectar un largo distinto de dos.
    extremos = list(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(f"un intervalo debe tener exactamente dos extremos: {intervalo!r}")
    inicio = _validar_extremo(extremos[0])
    fin = _validar_extremo(extremos[1])
    if inicio > fin:
        raise ValueError(f"el inicio no puede ser mayor que el fin: {intervalo!r}")
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    # Se valida todo antes de unir; la entrada sólo se recorre, nunca se modifica.
    validados = [_validar_intervalo(intervalo) for intervalo in iterador]
    validados.sort(key=lambda par: par[0])

    resultado = []
    for inicio, fin in validados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
