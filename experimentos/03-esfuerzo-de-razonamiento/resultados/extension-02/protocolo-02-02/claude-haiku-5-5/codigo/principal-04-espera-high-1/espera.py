import math


def _real_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _real_finito(base, "base")
    tope_f = _real_finito(tope, "tope")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")

    fraccion_f = _real_finito(fraccion, "fraccion")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base >= 2**-1074, así que para intento >= 2100 el producto supera
    # el máximo float y el mínimo es siempre tope. Evita exponentes enormes.
    if intento >= 2100:
        cota = tope_f
    else:
        try:
            cota = min(tope_f, math.ldexp(base_f, intento))
        except OverflowError:
            cota = tope_f

    return cota * fraccion_f
