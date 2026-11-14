import math


def _validar_extremo(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"extremo inválido: {valor!r}")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"extremo no finito: {valor!r}")
    return valor


def unir(intervalos):
    pares = []
    for intervalo in intervalos:
        if not isinstance(intervalo, (list, tuple)) or len(intervalo) != 2:
            raise ValueError(f"intervalo mal formado: {intervalo!r}")
        inicio = _validar_extremo(intervalo[0])
        fin = _validar_extremo(intervalo[1])
        if inicio > fin:
            raise ValueError(f"inicio mayor que fin: {intervalo!r}")
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
