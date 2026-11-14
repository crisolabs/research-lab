"""Unión de intervalos cerrados."""

import math
from operator import itemgetter

# Texto y bytes son iterables, pero nunca representan intervalos.
_TEXTO_O_BYTES = (str, bytes, bytearray, memoryview)


def _validar_extremo(valor, posicion):
    """Lanza ValueError si `valor` no es un int o float finito (bool excluido)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(
            f"intervalo en la posición {posicion}: extremo inválido de tipo "
            f"{type(valor).__name__}; se esperaba int o float"
        )
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(
            f"intervalo en la posición {posicion}: extremo no finito ({valor!r})"
        )


def _validar_intervalo(par, posicion):
    """Valida un intervalo y devuelve sus extremos como tupla (inicio, fin)."""
    if not isinstance(par, (list, tuple)):
        raise ValueError(
            f"intervalo en la posición {posicion}: se esperaba una lista o tupla "
            f"[inicio, fin], no {type(par).__name__}"
        )
    if len(par) != 2:
        raise ValueError(
            f"intervalo en la posición {posicion}: debe tener exactamente dos "
            f"extremos, no {len(par)}"
        )
    inicio, fin = par
    _validar_extremo(inicio, posicion)
    _validar_extremo(fin, posicion)
    if inicio > fin:
        raise ValueError(
            f"intervalo en la posición {posicion}: el inicio es mayor que el fin"
        )
    return inicio, fin


def unir(intervalos):
    """Une los intervalos cerrados que se superponen o se tocan.

    `intervalos` es cualquier iterable (que no se modifica) de listas o tuplas
    [inicio, fin], con extremos int o float finitos e inicio <= fin.
    Devuelve una lista nueva de listas [inicio, fin] disjuntas y ordenadas.
    Lanza ValueError si la entrada está mal formada.
    """
    if isinstance(intervalos, _TEXTO_O_BYTES):
        raise ValueError("se esperaba un iterable de intervalos, no texto ni bytes")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError(
            f"se esperaba un iterable de intervalos, no {type(intervalos).__name__}"
        ) from None

    # Se copian los extremos al validar: la entrada nunca se modifica ni se
    # comparte con el resultado.
    pares = [_validar_intervalo(par, i) for i, par in enumerate(iterador)]
    pares.sort(key=itemgetter(0))

    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            # Se superpone o toca con el último: extender su fin si hace falta.
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
