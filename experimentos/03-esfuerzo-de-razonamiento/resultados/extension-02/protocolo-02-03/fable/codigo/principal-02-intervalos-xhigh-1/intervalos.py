from collections.abc import Mapping, Set
from itertools import islice
from math import isfinite

# Tipos iterables que nunca representan un par ordenado [inicio, fin].
_TEXTO_O_BINARIO = (str, bytes, bytearray, memoryview)
_NO_ES_INTERVALO = _TEXTO_O_BINARIO + (Mapping, Set)


def _es_extremo_valido(valor):
    # bool es subclase de int, así que se descarta explícitamente.
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    return isinstance(valor, float) and isfinite(valor)


def _validar(intervalo):
    """Devuelve (inicio, fin) o lanza ValueError si el intervalo es inválido."""
    if isinstance(intervalo, _NO_ES_INTERVALO):
        raise ValueError(f"intervalo mal formado: {intervalo!r}")
    try:
        iterador = iter(intervalo)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {intervalo!r}") from None

    # Se leen como mucho tres elementos: alcanza para detectar un largo
    # incorrecto sin agotar iterables arbitrariamente largos.
    extremos = tuple(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(
            f"el intervalo debe tener exactamente dos extremos: {intervalo!r}"
        )

    inicio, fin = extremos
    for extremo in extremos:
        if not _es_extremo_valido(extremo):
            raise ValueError(f"extremo inválido: {extremo!r}")
    if inicio > fin:
        raise ValueError(f"el inicio es mayor que el fin: [{inicio!r}, {fin!r}]")
    return inicio, fin


def unir(intervalos):
    """Une intervalos cerrados superpuestos o que se tocan.

    Devuelve una lista nueva de listas ``[inicio, fin]`` ordenada, sin
    modificar la entrada. Lanza ``ValueError`` ante intervalos mal formados
    o extremos inválidos.
    """
    if isinstance(intervalos, _TEXTO_O_BINARIO):
        raise ValueError("la entrada debe ser un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    # Se valida todo antes de unir, para no devolver resultados parciales.
    pares = sorted(_validar(intervalo) for intervalo in iterador)

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
