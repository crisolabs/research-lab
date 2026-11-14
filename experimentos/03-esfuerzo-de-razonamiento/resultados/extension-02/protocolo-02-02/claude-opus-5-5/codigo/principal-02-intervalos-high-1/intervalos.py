import math
from collections.abc import Mapping, Set


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar_intervalo(par):
    if isinstance(par, (str, bytes, bytearray, Mapping, Set)):
        raise ValueError(f"intervalo mal formado: {par!r}")
    try:
        elementos = tuple(par)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {par!r}") from None
    if len(elementos) != 2:
        raise ValueError(f"el intervalo debe tener exactamente dos extremos: {par!r}")
    inicio = _validar_extremo(elementos[0])
    fin = _validar_extremo(elementos[1])
    if inicio > fin:
        raise ValueError(f"el inicio es mayor que el fin: {par!r}")
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    pares = [_validar_intervalo(par) for par in iterador]
    pares.sort(key=lambda p: (p[0], p[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
