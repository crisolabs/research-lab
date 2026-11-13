import math


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError as error:
        raise ValueError("Los intervalos deben ser iterables") from error

    validos = []
    centinela = object()

    for intervalo in iterador:
        try:
            extremos = iter(intervalo)
        except TypeError as error:
            raise ValueError("Cada intervalo debe contener dos extremos") from error

        try:
            inicio = next(extremos)
            fin = next(extremos)
        except StopIteration as error:
            raise ValueError("Cada intervalo debe contener dos extremos") from error

        if next(extremos, centinela) is not centinela:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser números enteros o flotantes")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("Los extremos deben ser finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")

        validos.append((inicio, fin))

    validos.sort(key=lambda intervalo: intervalo[0])

    unidos = []
    for inicio, fin in validos:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])

    return unidos
