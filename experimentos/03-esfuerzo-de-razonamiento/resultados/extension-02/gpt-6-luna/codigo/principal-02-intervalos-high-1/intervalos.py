import math


def unir(intervalos):
    try:
        entrada = iter(intervalos)
    except TypeError as error:
        raise ValueError("La entrada debe ser iterable") from error

    ordenados = []
    for intervalo in entrada:
        try:
            extremos = list(intervalo)
        except (TypeError, ValueError):
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")
        if len(extremos) != 2:
            raise ValueError("Cada intervalo debe contener exactamente dos extremos")
        inicio, fin = extremos

        if not _extremo_valido(inicio) or not _extremo_valido(fin) or inicio > fin:
            raise ValueError("Los extremos deben ser números finitos y estar ordenados")
        ordenados.append([inicio, fin])

    ordenados.sort(key=lambda par: (par[0], par[1]))
    unidos = []
    for inicio, fin in ordenados:
        if not unidos or inicio > unidos[-1][1]:
            unidos.append([inicio, fin])
        elif fin > unidos[-1][1]:
            unidos[-1][1] = fin
    return unidos


def _extremo_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return not isinstance(valor, float) or math.isfinite(valor)
