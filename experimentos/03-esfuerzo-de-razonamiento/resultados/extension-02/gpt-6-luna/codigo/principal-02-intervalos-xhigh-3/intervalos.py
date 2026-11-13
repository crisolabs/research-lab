from math import isfinite


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError as error:
        raise ValueError("La entrada debe ser iterable") from error

    ordenados = []
    for intervalo in iterador:
        try:
            extremos = list(intervalo)
        except TypeError as error:
            raise ValueError("Cada intervalo debe contener dos extremos") from error

        if len(extremos) != 2:
            raise ValueError("Cada intervalo debe contener dos extremos")

        inicio, fin = extremos
        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not isfinite(extremo):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")

        ordenados.append([inicio, fin])

    ordenados.sort(key=lambda intervalo: (intervalo[0], intervalo[1]))
    unidos = []
    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])

    return unidos
