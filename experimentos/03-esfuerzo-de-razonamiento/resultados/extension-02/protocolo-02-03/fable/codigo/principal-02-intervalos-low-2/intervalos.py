import math


def _es_numero(x):
    if isinstance(x, bool):
        return False
    if isinstance(x, int):
        return True
    if isinstance(x, float):
        return math.isfinite(x)
    return False


def _normalizar(par):
    if isinstance(par, (str, bytes, bytearray, set, frozenset, dict)):
        raise ValueError(f"intervalo mal formado: {par!r}")
    try:
        extremos = list(par)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {par!r}") from None
    if len(extremos) != 2:
        raise ValueError(f"intervalo mal formado: {par!r}")
    inicio, fin = extremos
    if not (_es_numero(inicio) and _es_numero(fin)):
        raise ValueError(f"extremos inválidos: {par!r}")
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {par!r}")
    return [inicio, fin]


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    normalizados = [_normalizar(par) for par in iterador]
    normalizados.sort(key=lambda p: (p[0], p[1]))

    resultado = []
    for inicio, fin in normalizados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
