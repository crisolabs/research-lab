import math


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def _validar_intervalo(par):
    if isinstance(par, (str, bytes)):
        raise ValueError(f"intervalo mal formado: {par!r}")
    try:
        partes = list(par)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {par!r}") from None
    if len(partes) != 2:
        raise ValueError(f"intervalo mal formado: {par!r}")
    inicio = _validar_extremo(partes[0])
    fin = _validar_extremo(partes[1])
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {par!r}")
    return inicio, fin


def unir(intervalos):
    validados = [_validar_intervalo(par) for par in intervalos]
    validados.sort(key=lambda iv: (iv[0], iv[1]))

    resultado = []
    for inicio, fin in validados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
