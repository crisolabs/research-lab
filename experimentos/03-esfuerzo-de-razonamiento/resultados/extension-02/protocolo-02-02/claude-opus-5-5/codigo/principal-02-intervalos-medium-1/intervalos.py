import math


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def unir(intervalos):
    if intervalos is None or isinstance(intervalos, (str, bytes, bytearray)):
        raise ValueError("se esperaba un iterable de intervalos")
    try:
        iterador = iter(intervalos)
    except TypeError:
        raise ValueError("se esperaba un iterable de intervalos") from None

    pares = []
    for par in iterador:
        if not isinstance(par, (list, tuple)) or len(par) != 2:
            raise ValueError(f"intervalo mal formado: {par!r}")
        inicio = _validar_extremo(par[0])
        fin = _validar_extremo(par[1])
        if inicio > fin:
            raise ValueError(f"inicio mayor que fin: {par!r}")
        pares.append((inicio, fin))

    pares.sort(key=lambda p: (p[0], p[1]))

    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
