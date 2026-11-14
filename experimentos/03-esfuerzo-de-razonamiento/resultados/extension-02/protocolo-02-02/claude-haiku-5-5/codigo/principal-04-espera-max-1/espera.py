import math


def _validar_numero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")


def _a_float_finito(valor, nombre):
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    _validar_numero(base, "base")
    _validar_numero(tope, "tope")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    b = _a_float_finito(base, "base")
    t = _a_float_finito(tope, "tope")
    _validar_numero(fraccion, "fraccion")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")
    f = float(fraccion)

    # Con b = mb * 2**eb y t = mt * 2**et (0.5 <= mb, mt < 1), b * 2**intento >= t
    # equivale a intento > et - eb, o a intento == et - eb con mb >= mt.
    # Así no se calcula 2**intento y ldexp solo se usa si el resultado es menor que t.
    mb, eb = math.frexp(b)
    mt, et = math.frexp(t)
    d = et - eb
    if intento > d or (intento == d and mb >= mt):
        return t * f
    return math.ldexp(b, intento) * f
