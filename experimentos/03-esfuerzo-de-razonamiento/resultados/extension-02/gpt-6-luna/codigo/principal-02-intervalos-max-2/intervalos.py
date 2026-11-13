import math


def unir(intervalos):
    try:
        iterator = iter(intervalos)
    except TypeError as error:
        raise ValueError("Los intervalos deben ser iterables") from error

    ordenados = []
    for intervalo in iterator:
        try:
            elementos = iter(intervalo)
            inicio = next(elementos)
            fin = next(elementos)
        except (TypeError, StopIteration) as error:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos") from error

        try:
            next(elementos)
        except StopIteration:
            pass
        else:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")
        ordenados.append((inicio, fin))

    ordenados.sort()
    unidos = []
    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
