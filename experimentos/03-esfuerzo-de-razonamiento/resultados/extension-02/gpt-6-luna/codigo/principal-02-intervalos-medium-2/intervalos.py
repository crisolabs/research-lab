import math


def unir(intervalos):
    try:
        elementos = iter(intervalos)
    except TypeError as exc:
        raise ValueError("intervalos debe ser un iterable") from exc

    ordenados = []
    for intervalo in elementos:
        try:
            extremos = list(intervalo)
        except TypeError as exc:
            raise ValueError("cada intervalo debe contener dos extremos") from exc

        if len(extremos) != 2:
            raise ValueError("cada intervalo debe contener dos extremos")

        inicio, fin = extremos
        for extremo in extremos:
            if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                raise ValueError("los extremos deben ser números enteros o flotantes")
            if isinstance(extremo, float) and not math.isfinite(extremo):
                raise ValueError("los extremos deben ser finitos")

        if inicio > fin:
            raise ValueError("el inicio no puede ser mayor que el fin")
        ordenados.append((inicio, fin))

    ordenados.sort(key=lambda par: (par[0], par[1]))
    resultado = []
    for inicio, fin in ordenados:
        if resultado and inicio <= resultado[-1][1]:
            resultado[-1][1] = max(resultado[-1][1], fin)
        else:
            resultado.append([inicio, fin])
    return resultado
