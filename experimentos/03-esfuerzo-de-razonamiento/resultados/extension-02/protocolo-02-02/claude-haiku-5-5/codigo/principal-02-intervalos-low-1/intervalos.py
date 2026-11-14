import math
import numbers


def _validar_extremo(x):
    if isinstance(x, bool) or not isinstance(x, numbers.Real):
        raise ValueError(f"extremo inválido: {x!r}")
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError(f"extremo no finito: {x!r}")
    return x


def _validar_intervalo(iv):
    if isinstance(iv, (str, bytes)):
        raise ValueError(f"intervalo mal formado: {iv!r}")
    try:
        partes = list(iv)
    except TypeError:
        raise ValueError(f"intervalo mal formado: {iv!r}") from None
    if len(partes) != 2:
        raise ValueError(f"intervalo mal formado: {iv!r}")
    inicio, fin = _validar_extremo(partes[0]), _validar_extremo(partes[1])
    if inicio > fin:
        raise ValueError(f"inicio mayor que fin: {iv!r}")
    return [inicio, fin]


def unir(intervalos):
    try:
        entrada = iter(intervalos)
    except TypeError:
        raise ValueError("se esperaba un iterable de intervalos") from None

    validados = [_validar_intervalo(iv) for iv in entrada]
    validados.sort(key=lambda p: (p[0], p[1]))

    resultado = []
    for inicio, fin in validados:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
