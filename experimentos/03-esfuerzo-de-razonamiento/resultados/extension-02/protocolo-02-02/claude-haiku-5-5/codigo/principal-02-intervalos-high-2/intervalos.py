import math


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _intervalo(iv):
    try:
        par = tuple(iv)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {iv!r}") from None
    if len(par) != 2:
        raise ValueError(f"intervalo mal formado: {iv!r}")
    inicio, fin = _extremo(par[0]), _extremo(par[1])
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {iv!r}")
    return inicio, fin


def unir(intervalos):
    validos = sorted(_intervalo(iv) for iv in intervalos)
    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
