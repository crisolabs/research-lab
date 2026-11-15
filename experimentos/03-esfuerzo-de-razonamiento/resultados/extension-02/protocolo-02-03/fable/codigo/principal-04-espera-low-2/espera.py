import math


def _numero_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser un número int o float")
    try:
        finito = math.isfinite(float(valor))
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError(f"{nombre} debe ser representable como float finito")


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")
    _numero_finito(base, "base")
    _numero_finito(tope, "tope")
    _numero_finito(fraccion, "fraccion")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base >= 2**-1074 y tope < 2**1024: con intento >= 2100 siempre se
    # alcanza el tope, sin necesidad de calcular la potencia.
    if intento >= 2100:
        valor = tope
    elif isinstance(base, int):
        valor = min(tope, base << intento)
    else:
        try:
            valor = min(tope, math.ldexp(base, intento))
        except OverflowError:
            valor = tope
    return valor * fraccion
