import math
from collections.abc import Mapping, Sequence

_TEXTO = (str, bytes, bytearray, memoryview)


def _es_extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return True


def _validar_intervalo(par):
    if isinstance(par, _TEXTO) or not isinstance(par, Sequence):
        raise ValueError(f"intervalo mal formado: {par!r}")
    try:
        extremos = tuple(par)
    except Exception as exc:
        raise ValueError(f"intervalo mal formado: {par!r}") from exc
    if len(extremos) != 2:
        raise ValueError(
            f"el intervalo debe tener exactamente dos extremos: {par!r}"
        )
    inicio, fin = extremos
    if not _es_extremo_valido(inicio) or not _es_extremo_valido(fin):
        raise ValueError(f"extremo inválido en el intervalo: {par!r}")
    if inicio > fin:
        raise ValueError(f"el inicio supera al fin en el intervalo: {par!r}")
    return inicio, fin


def unir(intervalos):
    if isinstance(intervalos, _TEXTO) or isinstance(intervalos, Mapping):
        raise ValueError("se esperaba un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError as exc:
        raise ValueError("se esperaba un iterable de intervalos") from exc

    pares = [_validar_intervalo(par) for par in iterador]
    pares.sort()

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
