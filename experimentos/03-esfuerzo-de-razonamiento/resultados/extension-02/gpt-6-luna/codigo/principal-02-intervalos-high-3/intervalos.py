from math import isfinite


def unir(intervalos):
    normalizados = []

    try:
        for intervalo in intervalos:
            try:
                extremos = tuple(intervalo)
            except TypeError as error:
                raise ValueError("cada intervalo debe contener dos extremos") from error

            if len(extremos) != 2:
                raise ValueError("cada intervalo debe contener exactamente dos extremos")

            inicio, fin = extremos
            for extremo in extremos:
                if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                    raise ValueError("los extremos deben ser enteros o flotantes finitos")
                if isinstance(extremo, float) and not isfinite(extremo):
                    raise ValueError("los extremos deben ser enteros o flotantes finitos")

            if inicio > fin:
                raise ValueError("el inicio no puede ser mayor que el fin")

            normalizados.append((inicio, fin))
    except TypeError as error:
        raise ValueError("la entrada debe ser iterable") from error

    normalizados.sort()
    unidos = []

    for inicio, fin in normalizados:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])

    return unidos
