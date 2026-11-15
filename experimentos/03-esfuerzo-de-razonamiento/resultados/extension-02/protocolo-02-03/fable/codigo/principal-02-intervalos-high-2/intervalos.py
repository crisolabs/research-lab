import math
from collections.abc import Mapping, Set
from itertools import islice

# Contenedores iterables que no representan un par ordenado de números.
_NO_SON_PARES = (str, bytes, bytearray, memoryview, Mapping, Set)


def _iterador(objeto, mensaje):
    try:
        return iter(objeto)
    except TypeError:
        raise ValueError(mensaje) from None


def _extremo_valido(valor):
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    return isinstance(valor, float) and math.isfinite(valor)


def _validar(intervalo):
    if isinstance(intervalo, _NO_SON_PARES):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    iterador = _iterador(intervalo, f"intervalo mal formado: {intervalo!r}")
    # Con tres elementos alcanza para saber que no son exactamente dos.
    extremos = list(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(
            f"intervalo mal formado (debe tener exactamente dos extremos): {intervalo!r}"
        )
    inicio, fin = extremos
    for extremo in extremos:
        if not _extremo_valido(extremo):
            raise ValueError(f"extremo inválido: {extremo!r}")
    if inicio > fin:
        raise ValueError(f"el inicio es mayor que el fin: {extremos!r}")
    return inicio, fin


def unir(intervalos):
    iterador = _iterador(intervalos, "se esperaba un iterable de intervalos")
    pares = [_validar(intervalo) for intervalo in iterador]
    pares.sort()

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
