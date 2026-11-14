import math


def _extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("extremo inválido: %r" % (valor,))
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError("extremo no finito: %r" % (valor,))
    return valor


def unir(intervalos):
    if intervalos is None or isinstance(intervalos, (str, bytes, bytearray)):
        raise ValueError("entrada inválida")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("la entrada debe ser iterable") from None

    pares = []
    for par in iterador:
        if isinstance(par, (str, bytes, bytearray, dict, set, frozenset)):
            raise ValueError("intervalo mal formado: %r" % (par,))
        try:
            elementos = list(par)
        except TypeError:
            raise ValueError("intervalo mal formado: %r" % (par,)) from None
        if len(elementos) != 2:
            raise ValueError("el intervalo debe tener exactamente dos extremos")
        inicio, fin = _extremo(elementos[0]), _extremo(elementos[1])
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
