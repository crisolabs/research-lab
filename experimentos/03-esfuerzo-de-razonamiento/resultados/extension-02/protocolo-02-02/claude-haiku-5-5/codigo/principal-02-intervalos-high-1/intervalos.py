import math


def _es_numero(valor):
    """Devuelve True si valor es un int o float finito (no bool)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return True


def _validar(intervalo):
    """Valida un intervalo y devuelve la tupla (inicio, fin)."""
    try:
        partes = list(intervalo)
    except TypeError:
        raise ValueError(f"intervalo no iterable: {intervalo!r}") from None

    if len(partes) != 2:
        raise ValueError(f"el intervalo debe tener exactamente 2 extremos: {intervalo!r}")

    inicio, fin = partes
    if not (_es_numero(inicio) and _es_numero(fin)):
        raise ValueError(f"extremos inválidos en el intervalo: {intervalo!r}")
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin en el intervalo: {intervalo!r}")

    return inicio, fin


def unir(intervalos):
    """Une intervalos cerrados superpuestos o que se tocan.

    Devuelve una lista de [inicio, fin] ordenada. No modifica la entrada.
    Lanza ValueError ante intervalos mal formados o extremos inválidos.
    """
    try:
        entrada = list(intervalos)
    except TypeError:
        raise ValueError(f"la entrada no es iterable: {intervalos!r}") from None

    validos = [_validar(intervalo) for intervalo in entrada]
    validos.sort(key=lambda par: par[0])

    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
