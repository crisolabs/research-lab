import math
from collections.abc import Iterable, Mapping, Set


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _normalizar(intervalo):
    if (
        isinstance(intervalo, (str, bytes, bytearray, Mapping, Set))
        or not isinstance(intervalo, Iterable)
    ):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        extremos = tuple(intervalo)
    except TypeError as exc:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from exc
    if len(extremos) != 2:
        raise ValueError(f"el intervalo debe tener dos extremos: {intervalo!r}")
    inicio = _validar_extremo(extremos[0])
    fin = _validar_extremo(extremos[1])
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {intervalo!r}")
    return inicio, fin


def unir(intervalos):
    pares = [_normalizar(intervalo) for intervalo in intervalos]
    pares.sort(key=lambda par: (par[0], par[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
