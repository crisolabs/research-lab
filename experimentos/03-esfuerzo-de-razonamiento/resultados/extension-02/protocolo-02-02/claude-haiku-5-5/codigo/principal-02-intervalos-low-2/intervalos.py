import math


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _intervalo(par):
    try:
        elementos = list(par)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {par!r}") from None
    if len(elementos) != 2:
        raise ValueError(f"intervalo mal formado: {par!r}")
    inicio, fin = (_extremo(e) for e in elementos)
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {par!r}")
    return [inicio, fin]


def unir(intervalos):
    try:
        entrada = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada no es un iterable") from None

    validos = [_intervalo(par) for par in entrada]
    validos.sort(key=lambda iv: (iv[0], iv[1]))

    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
