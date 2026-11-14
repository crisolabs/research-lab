import math


def _validar_extremo(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError("extremo inválido: %r" % (x,))
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError("extremo no finito: %r" % (x,))
    return x


def unir(intervalos):
    if intervalos is None:
        raise ValueError("entrada inválida")
    try:
        items = list(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser iterable")

    pares = []
    for par in items:
        if isinstance(par, (str, bytes, bytearray, dict)):
            raise ValueError("intervalo mal formado: %r" % (par,))
        try:
            elems = tuple(par)
        except TypeError:
            raise ValueError("intervalo mal formado: %r" % (par,))
        if len(elems) != 2:
            raise ValueError("intervalo mal formado: %r" % (par,))
        a = _validar_extremo(elems[0])
        b = _validar_extremo(elems[1])
        if a > b:
            raise ValueError("inicio mayor que fin: %r" % (par,))
        pares.append((a, b))

    pares.sort()
    resultado = []
    for a, b in pares:
        if resultado and a <= resultado[-1][1]:
            if b > resultado[-1][1]:
                resultado[-1][1] = b
        else:
            resultado.append([a, b])
    return resultado
