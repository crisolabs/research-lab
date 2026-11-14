import math


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("extremo inválido: %r" % (valor,))
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError("extremo no finito: %r" % (valor,))
    return valor


def unir(intervalos):
    if intervalos is None:
        raise ValueError("entrada inválida")
    try:
        elementos = list(intervalos)
    except TypeError:
        raise ValueError("la entrada no es iterable") from None

    pares = []
    for par in elementos:
        if isinstance(par, (str, bytes, bytearray, dict, set, frozenset)):
            raise ValueError("intervalo mal formado: %r" % (par,))
        try:
            valores = list(par)
        except TypeError:
            raise ValueError("intervalo mal formado: %r" % (par,)) from None
        if len(valores) != 2:
            raise ValueError("intervalo mal formado: %r" % (par,))
        inicio, fin = _extremo(valores[0]), _extremo(valores[1])
        if inicio > fin:
            raise ValueError("inicio mayor que fin: %r" % (par,))
        pares.append((inicio, fin))

    pares.sort()
    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
