import math


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError as error:
        raise ValueError("Se esperaba un iterable de intervalos") from error

    ordenados = []
    for intervalo in iterador:
        try:
            inicio, fin = intervalo
        except (TypeError, ValueError) as error:
            raise ValueError("Cada intervalo debe contener dos extremos") from error

        for extremo in (inicio, fin):
            if (
                isinstance(extremo, bool)
                or not isinstance(extremo, (int, float))
                or (isinstance(extremo, float) and not math.isfinite(extremo))
            ):
                raise ValueError("Los extremos deben ser números finitos")
        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")
        ordenados.append([inicio, fin])

    ordenados.sort(key=lambda intervalo: intervalo[0])
    unidos = []
    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
