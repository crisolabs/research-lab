import math


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar(intervalo):
    try:
        partes = list(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    if len(partes) != 2:
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    inicio, fin = _extremo(partes[0]), _extremo(partes[1])
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {intervalo!r}")
    return [inicio, fin]


def unir(intervalos):
    validados = sorted((_validar(i) for i in intervalos), key=lambda p: (p[0], p[1]))
    resultado = []
    for inicio, fin in validados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
