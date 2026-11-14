import math


def _extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _normalizar(intervalo):
    try:
        partes = list(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    if len(partes) != 2:
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    inicio, fin = (_extremo_valido(p) for p in partes)
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {intervalo!r}")
    return [inicio, fin]


def unir(intervalos):
    normalizados = [_normalizar(intervalo) for intervalo in intervalos]
    normalizados.sort(key=lambda par: (par[0], par[1]))

    resultado = []
    for inicio, fin in normalizados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
