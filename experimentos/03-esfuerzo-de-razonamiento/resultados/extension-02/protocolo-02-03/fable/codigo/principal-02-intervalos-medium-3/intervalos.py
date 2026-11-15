import math
from itertools import islice


def _extremo_valido(x):
    if isinstance(x, bool):
        return False
    if isinstance(x, int):
        return True
    if isinstance(x, float):
        return math.isfinite(x)
    return False


def unir(intervalos):
    if isinstance(intervalos, (str, bytes, bytearray)):
        raise ValueError("la entrada debe ser un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    pares = []
    for par in iterador:
        if isinstance(par, (str, bytes, bytearray, dict, set, frozenset)):
            raise ValueError(f"intervalo mal formado: {par!r}")
        try:
            # islice evita colgarse con un iterable infinito como intervalo.
            extremos = list(islice(iter(par), 3))
        except TypeError:
            raise ValueError(f"intervalo mal formado: {par!r}") from None
        if len(extremos) != 2:
            raise ValueError(f"intervalo mal formado: {par!r}")
        inicio, fin = extremos
        if not (_extremo_valido(inicio) and _extremo_valido(fin)):
            raise ValueError(f"extremos inválidos: {par!r}")
        if inicio > fin:
            raise ValueError(f"inicio mayor que fin: {par!r}")
        pares.append((inicio, fin))

    pares.sort()

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
