import math


def unir(intervalos):
    pares = []

    try:
        iterator = iter(intervalos)
    except TypeError as exc:
        raise ValueError("intervalos debe ser iterable") from exc

    for intervalo in iterator:
        try:
            extremos = iter(intervalo)
            inicio = next(extremos)
            fin = next(extremos)
        except (TypeError, StopIteration):
            raise ValueError("cada intervalo debe contener exactamente dos extremos") from None
        try:
            next(extremos)
        except StopIteration:
            pass
        else:
            raise ValueError("cada intervalo debe contener exactamente dos extremos")

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("los extremos deben ser enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("el inicio no puede ser mayor que el fin")
        pares.append((inicio, fin))

    pares.sort(key=lambda par: par[0])
    unidos = []
    for inicio, fin in pares:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin

    return unidos
