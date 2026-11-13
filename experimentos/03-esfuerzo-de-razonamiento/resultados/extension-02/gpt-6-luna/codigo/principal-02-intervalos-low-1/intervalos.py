import math


def unir(intervalos):
    normalizados = []

    for intervalo in intervalos:
        try:
            extremos = list(intervalo)
        except (TypeError, ValueError):
            raise ValueError("Cada intervalo debe contener dos extremos") from None

        if len(extremos) != 2:
            raise ValueError("Cada intervalo debe contener dos extremos")

        inicio, fin = extremos
        if (isinstance(inicio, bool) or not isinstance(inicio, (int, float)) or
                isinstance(fin, bool) or not isinstance(fin, (int, float))):
            raise ValueError("Los extremos deben ser números enteros o flotantes finitos")

        if (isinstance(inicio, float) and not math.isfinite(inicio) or
                isinstance(fin, float) and not math.isfinite(fin)):
            raise ValueError("Los extremos deben ser números enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")

        normalizados.append([inicio, fin])

    normalizados.sort(key=lambda par: (par[0], par[1]))
    unidos = []
    for inicio, fin in normalizados:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin

    return unidos
