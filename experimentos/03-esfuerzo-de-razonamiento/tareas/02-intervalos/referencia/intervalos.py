import math


def unir(intervalos):
    try:
        pares = [list(p) for p in intervalos]
    except TypeError as error:
        raise ValueError("intervalo inválido") from error
    if any(len(p) != 2 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or (isinstance(x, float) and not math.isfinite(x)) for x in p) or p[0] > p[1] for p in pares):
        raise ValueError("intervalo inválido")
    salida = []
    for a, b in sorted(pares):
        if salida and a <= salida[-1][1]:
            salida[-1][1] = max(salida[-1][1], b)
        else:
            salida.append([a, b])
    return salida
