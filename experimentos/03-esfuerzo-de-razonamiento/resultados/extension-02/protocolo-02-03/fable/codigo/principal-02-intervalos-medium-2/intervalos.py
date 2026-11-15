import math


def _extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return not isinstance(valor, float) or math.isfinite(valor)


def _validar(intervalo):
    if isinstance(intervalo, (str, bytes, bytearray, dict, set, frozenset)):
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
        raise ValueError(f"el inicio es mayor que el fin: {par!r}")
    return par


def unir(intervalos):
    if isinstance(intervalos, (str, bytes, bytearray)):
        raise ValueError("la entrada debe ser un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    pares = sorted(_validar(intervalo) for intervalo in iterador)

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
