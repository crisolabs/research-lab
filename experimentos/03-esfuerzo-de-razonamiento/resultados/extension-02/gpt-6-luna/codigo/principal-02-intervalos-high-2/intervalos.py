import math


def unir(intervalos):
    ordenados = []

    for intervalo in intervalos:
        try:
            par = tuple(intervalo)
        except TypeError as error:
            raise ValueError("cada intervalo debe contener dos extremos") from error

        if len(par) != 2:
            raise ValueError("cada intervalo debe contener exactamente dos extremos")

        inicio, fin = par
        for extremo in par:
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("los extremos deben ser números enteros o flotantes finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("los extremos deben ser números enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("el inicio debe ser menor o igual al fin")

        ordenados.append([inicio, fin])

    ordenados.sort(key=lambda intervalo: (intervalo[0], intervalo[1]))
    unidos = []

    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])

    return unidos
