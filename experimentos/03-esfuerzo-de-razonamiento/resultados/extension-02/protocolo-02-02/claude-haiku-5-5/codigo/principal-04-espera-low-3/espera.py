import math


def _real_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")
    try:
        f = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")
    return f


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero no negativo")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _real_finito(base, "base")
    tope_f = _real_finito(tope, "tope")
    if not (0 < base_f <= tope_f):
        raise ValueError("se requiere 0 < base <= tope")

    frac_f = _real_finito(fraccion, "fraccion")
    if not (0 <= frac_f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # El menor base positivo es 2**-1074 y el mayor float es < 2**1024, así que
    # para intento >= 2100 el término exponencial supera siempre a tope.
    if intento >= 2100:
        return tope_f * frac_f

    try:
        crecimiento = math.ldexp(base_f, intento)  # base * 2**intento, exacto
    except OverflowError:
        crecimiento = math.inf

    return min(tope_f, crecimiento) * frac_f
