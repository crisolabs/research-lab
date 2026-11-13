import math


def unir(intervalos):
    validos = []

    for intervalo in intervalos:
        try:
            extremos = list(intervalo)
        except TypeError as error:
            raise ValueError("cada intervalo debe contener dos extremos") from error

        if len(extremos) != 2:
            raise ValueError("cada intervalo debe contener dos extremos")

        inicio, fin = extremos
        for extremo in extremos:
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("los extremos deben ser números finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("los extremos deben ser números finitos")

        if inicio > fin:
            raise ValueError("el inicio no puede ser mayor que el fin")

        validos.append([inicio, fin])

    validos.sort(key=lambda intervalo: (intervalo[0], intervalo[1]))
    unidos = []

    for inicio, fin in validos:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin

    return unidos
