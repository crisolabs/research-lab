import math
from collections.abc import Mapping, Set


def _extremo_valido(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    return not isinstance(x, float) or math.isfinite(x)


def _normalizar(intervalo):
    if isinstance(intervalo, (str, bytes, bytearray, Mapping, Set)):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        par = list(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    if len(par) != 2:
        raise ValueError(f"el intervalo debe tener exactamente dos extremos: {par!r}")
    inicio, fin = par
    if not (_extremo_valido(inicio) and _extremo_valido(fin)):
        raise ValueError(f"extremos inválidos: {par!r}")
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {par!r}")
    return par


def unir(intervalos):
    if isinstance(intervalos, (str, bytes, bytearray, Mapping)):
        raise ValueError("la entrada debe ser un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    pares = [_normalizar(intervalo) for intervalo in iterador]
    pares.sort(key=lambda par: (par[0], par[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
