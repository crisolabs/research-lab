import math


def _es_numero(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return not isinstance(valor, float) or math.isfinite(valor)


def _validar(intervalo):
    if not isinstance(intervalo, (list, tuple)) or len(intervalo) != 2:
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    inicio, fin = intervalo
    if not (_es_numero(inicio) and _es_numero(fin)):
        raise ValueError(f"extremos inválidos: {intervalo!r}")
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {intervalo!r}")
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    validos = sorted(_validar(intervalo) for intervalo in iterador)

    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
