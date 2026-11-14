import math


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar_intervalo(intervalo):
    if isinstance(intervalo, (str, bytes, bytearray)):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        partes = tuple(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None
    if len(partes) != 2:
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    inicio, fin = (_validar_extremo(p) for p in partes)
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {intervalo!r}")
    return inicio, fin


def unir(intervalos):
    # Se validan todos los intervalos antes de operar; no se modifica la entrada.
    pares = sorted(_validar_intervalo(intervalo) for intervalo in intervalos)

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            # Solapados o contiguos (cerrados): se extiende el bloque actual.
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
