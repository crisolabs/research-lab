import math


def _validar_real(x, nombre):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float no booleano")
    if isinstance(x, float) and not math.isfinite(x):
        raise ValueError(f"{nombre} debe ser finito")


def _como_float_finito(x, nombre):
    try:
        f = float(x)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float") from None
    if not math.isfinite(f):
        raise ValueError(f"{nombre} no es representable como float finito")
    return f


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    _validar_real(base, "base")
    _validar_real(tope, "tope")
    base_f = _como_float_finito(base, "base")
    tope_f = _como_float_finito(tope, "tope")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")

    _validar_real(fraccion, "fraccion")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base * 2**intento = mb * 2**e, con e = eb + intento.
    # Comparar exponentes evita construir 2**intento (que puede ser enorme).
    mb, eb = math.frexp(base_f)
    mt, et = math.frexp(tope_f)
    e = eb + intento
    if e > et or (e == et and mb >= mt):
        # base * 2**intento >= tope, así que el mínimo es tope.
        valor = tope_f
    else:
        # Aquí base * 2**intento < tope <= máximo float: ldexp es exacto.
        valor = math.ldexp(mb, e)
    return valor * fraccion
