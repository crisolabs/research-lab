import math

# Límite por encima del cual 2**intento supera cualquier float finito
# (el mayor float finito es ~1.8e308 < 2**1024).
_LIMITE_INTENTO = 1100


def _float_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no {type(valor).__name__}")
    try:
        f = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")
    return f


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero no negativo")
    if intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    base_f = _float_finito(base, "base")
    tope_f = _float_finito(tope, "tope")
    if not (0 < base_f <= tope_f):
        raise ValueError("se requiere 0 < base <= tope")

    frac_f = _float_finito(fraccion, "fraccion")
    if not (0 <= frac_f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base * 2**intento sin construir enteros gigantes: si el exponente es
    # enorme, el valor supera tope; si desborda float, también supera tope.
    if intento >= _LIMITE_INTENTO:
        exponencial = tope_f
    else:
        try:
            exponencial = math.ldexp(base_f, intento)
        except OverflowError:
            exponencial = math.inf

    return min(tope_f, exponencial) * frac_f
