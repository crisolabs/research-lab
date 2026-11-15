import math
from collections.abc import Mapping, Set
from itertools import islice

# Tipos iterables que no representan un par ordenado de números.
_NO_SON_INTERVALOS = (str, bytes, bytearray, memoryview, Set, Mapping)


def _validar_extremo(valor, posicion):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(
            f"intervalo {posicion}: extremo de tipo inválido "
            f"({type(valor).__name__})"
        )
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"intervalo {posicion}: extremo no finito ({valor!r})")
    return valor


def _leer_intervalo(intervalo, posicion):
    if isinstance(intervalo, _NO_SON_INTERVALOS):
        raise ValueError(
            f"intervalo {posicion}: tipo inválido ({type(intervalo).__name__})"
        )
    try:
        iterador = iter(intervalo)
    except TypeError:
        raise ValueError(
            f"intervalo {posicion}: tipo inválido ({type(intervalo).__name__})"
        ) from None

    # Con tres elementos alcanza para saber que sobra alguno, sin agotar
    # un iterador potencialmente infinito.
    extremos = list(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(
            f"intervalo {posicion}: debe tener exactamente dos extremos"
        )

    inicio = _validar_extremo(extremos[0], posicion)
    fin = _validar_extremo(extremos[1], posicion)
    if inicio > fin:
        raise ValueError(f"intervalo {posicion}: el inicio es mayor que el fin")
    return [inicio, fin]


def unir(intervalos):
    """Une intervalos cerrados que se superponen o se tocan.

    Devuelve una lista nueva de listas ``[inicio, fin]`` ordenada por inicio.
    Lanza ``ValueError`` si la entrada o alguno de sus intervalos es inválido.
    """
    if isinstance(intervalos, (str, bytes, bytearray, memoryview)):
        raise ValueError(
            f"entrada inválida: se esperaba un iterable de intervalos, "
            f"no {type(intervalos).__name__}"
        )
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError(
            f"entrada inválida: se esperaba un iterable de intervalos, "
            f"no {type(intervalos).__name__}"
        ) from None

    pares = [
        _leer_intervalo(intervalo, posicion)
        for posicion, intervalo in enumerate(iterador)
    ]
    pares.sort(key=lambda par: par[0])

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
