import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento inválido")
    try:
        invalidos = any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in (base, tope, fraccion)) or not 0 < base <= tope or not 0 <= fraccion <= 1
    except OverflowError as error:
        raise ValueError("parámetros inválidos") from error
    if invalidos:
        raise ValueError("parámetros inválidos")
    if intento >= max(0, math.ceil(math.log2(tope) - math.log2(base))):
        return tope * fraccion
    return min(tope, math.ldexp(base, intento)) * fraccion
