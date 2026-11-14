import math


def _real_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
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

    base = _real_finito(base, "base")
    tope = _real_finito(tope, "tope")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")

    fraccion = _real_finito(fraccion, "fraccion")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # Descomposición exacta: base = mb * 2**eb, tope = mt * 2**et, con 0.5 <= m < 1.
    # base * 2**intento = mb * 2**(eb + intento); se compara sin construir números gigantes.
    mb, eb = math.frexp(base)
    mt, et = math.frexp(tope)
    exponente = eb + intento
    if exponente > et or (exponente == et and mb >= mt):
        # base * 2**intento >= tope
        valor = tope
    else:
        # base * 2**intento < tope <= max float: ldexp no desborda
        valor = math.ldexp(base, intento)

    return valor * fraccion
