import math


def unir(intervalos):
    validados = []

    try:
        iterador = iter(intervalos)
    except TypeError as error:
        raise ValueError("La entrada debe ser iterable") from error

    for intervalo in iterador:
        try:
            extremos = list(intervalo)
        except TypeError as error:
            raise ValueError("Cada intervalo debe contener dos extremos") from error

        if len(extremos) != 2:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")

        inicio, fin = extremos
        for extremo in extremos:
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")

        validados.append((inicio, fin))

    validados.sort()
    unidos = []
    for inicio, fin in validados:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])

    return unidos
