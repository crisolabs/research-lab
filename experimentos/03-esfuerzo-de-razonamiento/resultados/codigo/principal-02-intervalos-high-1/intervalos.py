from math import isfinite


def unir(intervalos):
    try:
        entrada = iter(intervalos)
    except TypeError as exc:
        raise ValueError("Los intervalos deben ser un iterable") from exc

    ordenados = []
    for intervalo in entrada:
        try:
            inicio, fin = intervalo
        except (TypeError, ValueError) as exc:
            raise ValueError("Cada intervalo debe contener dos extremos") from exc

        for extremo in (inicio, fin):
            if (
                isinstance(extremo, bool)
                or not isinstance(extremo, (int, float))
                or (isinstance(extremo, float) and not isfinite(extremo))
            ):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
        if inicio > fin:
            raise ValueError("El inicio debe ser menor o igual al fin")
        ordenados.append([inicio, fin])

    ordenados.sort()
    unidos = []
    for inicio, fin in ordenados:
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fin)
        else:
            unidos.append([inicio, fin])
    return unidos
