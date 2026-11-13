import math


def unir(intervalos):
    try:
        intervalos = iter(intervalos)
    except TypeError as error:
        raise ValueError("La entrada debe ser iterable") from error

    ordenados = []
    marcador = object()
    for intervalo in intervalos:
        try:
            valores = iter(intervalo)
        except TypeError as error:
            raise ValueError("Cada intervalo debe ser iterable") from error

        inicio = next(valores, marcador)
        fin = next(valores, marcador)
        extra = next(valores, marcador)
        if inicio is marcador or fin is marcador or extra is not marcador:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")

        for extremo in (inicio, fin):
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("Los extremos deben ser enteros o flotantes finitos")
            if isinstance(extremo, float):
                try:
                    finito = math.isfinite(extremo)
                except (TypeError, ValueError, OverflowError) as error:
                    raise ValueError("Los extremos deben ser enteros o flotantes finitos") from error
                if not finito:
                    raise ValueError("Los extremos deben ser enteros o flotantes finitos")

        if inicio > fin:
            raise ValueError("El inicio no puede ser mayor que el fin")
        ordenados.append((inicio, fin))

    ordenados.sort()
    resultado = []
    for inicio, fin in ordenados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])

    return resultado
