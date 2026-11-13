from math import isfinite


def unir(intervalos):
    try:
        entrada = iter(intervalos)
    except TypeError as exc:
        raise ValueError("La entrada debe ser un iterable de intervalos") from exc

    ordenados = []
    for par in entrada:
        try:
            inicio, fin = par
        except (TypeError, ValueError) as exc:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos") from exc

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not isfinite(extremo):
                raise ValueError("Los extremos deben ser finitos")
        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")
        ordenados.append([inicio, fin])

    ordenados.sort()
    unidos = []
    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
