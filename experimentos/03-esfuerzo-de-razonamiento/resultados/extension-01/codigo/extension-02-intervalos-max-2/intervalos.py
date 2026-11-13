from math import isfinite


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError as exc:
        raise ValueError("La entrada debe ser un iterable de intervalos.") from exc

    ordenados = []
    for intervalo in iterador:
        try:
            inicio, fin = intervalo
        except (TypeError, ValueError) as exc:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos.") from exc

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos.")
            if isinstance(extremo, float) and not isfinite(extremo):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos.")
        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin.")

        ordenados.append([inicio, fin])

    ordenados.sort(key=lambda intervalo: intervalo[0])
    unidos = []
    for inicio, fin in ordenados:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin
    return unidos
