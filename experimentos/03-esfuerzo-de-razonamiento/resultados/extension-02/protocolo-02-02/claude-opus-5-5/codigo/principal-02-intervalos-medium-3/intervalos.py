import math
from collections.abc import Iterable, Sequence


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar_intervalo(par):
    if not isinstance(par, Sequence) or isinstance(par, (str, bytes, bytearray)):
        raise ValueError(f"intervalo mal formado: {par!r}")
    if len(par) != 2:
        raise ValueError(f"el intervalo debe tener exactamente dos extremos: {par!r}")
    inicio = _validar_extremo(par[0])
    fin = _validar_extremo(par[1])
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {par!r}")
    return inicio, fin


def unir(intervalos):
    if intervalos is None or not isinstance(intervalos, Iterable) or isinstance(
        intervalos, (str, bytes, bytearray)
    ):
        raise ValueError("se esperaba un iterable de intervalos")

    pares = [_validar_intervalo(par) for par in intervalos]
    pares.sort(key=lambda p: (p[0], p[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
