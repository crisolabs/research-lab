import math
from collections.abc import Sequence


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _intervalo(par):
    if not isinstance(par, Sequence) or isinstance(par, (str, bytes, bytearray)):
        raise ValueError(f"intervalo mal formado: {par!r}")
    if len(par) != 2:
        raise ValueError(f"intervalo mal formado: {par!r}")
    inicio = _extremo(par[0])
    fin = _extremo(par[1])
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {par!r}")
    return inicio, fin


def unir(intervalos):
    validos = sorted(_intervalo(par) for par in intervalos)
    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
