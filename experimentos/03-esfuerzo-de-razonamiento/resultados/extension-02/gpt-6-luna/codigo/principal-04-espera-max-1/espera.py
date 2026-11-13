import math


def _float_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError

    try:
        convertido = float(valor)
    except (OverflowError, TypeError, ValueError):
        raise ValueError from None

    if not math.isfinite(convertido):
        raise ValueError
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError

    base_float = _float_finito(base)
    tope_float = _float_finito(tope)
    fraccion_float = _float_finito(fraccion)

    if not (0 < base <= tope) or not (0 <= fraccion <= 1):
        raise ValueError

    valor = base_float
    pasos = 0
    while pasos < intento and valor < tope_float:
        valor *= 2.0
        if valor >= tope_float:
            valor = tope_float
            break
        pasos += 1

    return valor * fraccion_float
