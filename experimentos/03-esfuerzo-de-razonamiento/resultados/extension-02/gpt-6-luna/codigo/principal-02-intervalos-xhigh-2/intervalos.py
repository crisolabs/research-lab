import math


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser iterable") from None

    validos = []
    for intervalo in iterador:
        if isinstance(intervalo, (str, bytes, bytearray)):
            raise ValueError("cada intervalo debe contener dos extremos numéricos")

        try:
            extremos = iter(intervalo)
        except TypeError:
            raise ValueError("cada intervalo debe contener dos extremos numéricos") from None

        try:
            inicio = next(extremos)
            fin = next(extremos)
        except (StopIteration, TypeError):
            raise ValueError("cada intervalo debe contener exactamente dos extremos") from None

        try:
            next(extremos)
        except StopIteration:
            pass
        except TypeError:
            raise ValueError("cada intervalo debe contener exactamente dos extremos") from None
        else:
            raise ValueError("cada intervalo debe contener exactamente dos extremos")

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("los extremos deben ser enteros o flotantes finitos")

        try:
            if inicio > fin:
                raise ValueError("el inicio no puede ser mayor que el fin")
        except TypeError:
            raise ValueError("los extremos deben poder compararse") from None

        validos.append([inicio, fin])

    validos.sort()
    unidos = []
    for inicio, fin in validos:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin

    return unidos
