import math


def _es_extremo_valido(valor):
    # bool es subclase de int, por eso se descarta de forma explícita.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    # Sólo los flotantes pueden ser nan/inf; isfinite sobre enteros enormes
    # desbordaría al convertirlos a float.
    return not isinstance(valor, float) or math.isfinite(valor)


def _validar(posicion, intervalo):
    if not isinstance(intervalo, (list, tuple)) or len(intervalo) != 2:
        raise ValueError(
            f"intervalo mal formado en la posición {posicion}: "
            "se esperaba una lista o tupla de dos números"
        )
    inicio, fin = intervalo
    if not (_es_extremo_valido(inicio) and _es_extremo_valido(fin)):
        raise ValueError(
            f"extremos inválidos en la posición {posicion}: "
            "deben ser enteros o flotantes finitos"
        )
    if inicio > fin:
        raise ValueError(
            f"intervalo invertido en la posición {posicion}: "
            "el inicio no puede ser mayor que el fin"
        )
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser un iterable de intervalos") from None

    # Se copian los extremos a tuplas propias: la entrada nunca se toca.
    pares = [_validar(posicion, intervalo) for posicion, intervalo in enumerate(iterador)]
    pares.sort()

    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
