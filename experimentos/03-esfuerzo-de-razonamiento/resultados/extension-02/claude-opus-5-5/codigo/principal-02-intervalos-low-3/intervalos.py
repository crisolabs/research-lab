import math


def _validar_extremo(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError("extremo inválido")
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError("extremo no finito")
    return x


def unir(intervalos):
    if intervalos is None:
        raise ValueError("entrada inválida")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("entrada no iterable")

    pares = []
    for par in iterador:
        if isinstance(par, (str, bytes, dict, set, frozenset)):
            raise ValueError("intervalo mal formado")
        try:
            elementos = list(par)
        except TypeError:
            raise ValueError("intervalo mal formado")
        if len(elementos) != 2:
            raise ValueError("intervalo mal formado")
        inicio = _validar_extremo(elementos[0])
        fin = _validar_extremo(elementos[1])
        if inicio > fin:
            raise ValueError("inicio mayor que fin")
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
