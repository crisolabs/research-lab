import math
from collections.abc import Mapping, Set
from itertools import islice

__all__ = ["unir"]

# Iterables que no representan un par ordenado [inicio, fin]: texto, datos
# binarios y colecciones sin un orden propio de extremos.
_NO_SON_PARES = (str, bytes, bytearray, memoryview, Set, Mapping)


def _es_extremo(valor):
    # bool es subclase de int: hay que descartarlo antes de aceptar enteros.
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    return isinstance(valor, float) and math.isfinite(valor)


def _extremos(intervalo, posicion):
    if isinstance(intervalo, _NO_SON_PARES):
        raise ValueError(
            f"intervalos[{posicion}] mal formado: se esperaba un par [inicio, fin]"
        )
    try:
        iterador = iter(intervalo)
    except TypeError:
        raise ValueError(
            f"intervalos[{posicion}] mal formado: se esperaba un par [inicio, fin]"
        ) from None

    # Con leer hasta tres elementos alcanza para saber si son exactamente dos.
    extremos = tuple(islice(iterador, 3))
    if len(extremos) != 2:
        raise ValueError(
            f"intervalos[{posicion}] mal formado: debe contener exactamente dos extremos"
        )

    inicio, fin = extremos
    if not (_es_extremo(inicio) and _es_extremo(fin)):
        raise ValueError(
            f"intervalos[{posicion}] tiene un extremo inválido: "
            "deben ser enteros o flotantes finitos, no booleanos"
        )
    if inicio > fin:
        raise ValueError(
            f"intervalos[{posicion}] tiene el inicio mayor que el fin"
        )
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    pares = [
        _extremos(intervalo, posicion)
        for posicion, intervalo in enumerate(iterador)
    ]
    pares.sort()

    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
