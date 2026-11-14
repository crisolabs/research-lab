import math
from fractions import Fraction

# base >= 2**-1074 (menor float positivo) y tope < 2**1024, así que para
# intento >= 2098 se cumple base * 2**intento > tope. 2100 deja margen.
_INTENTO_SATURACION = 2100


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _a_float_finito(valor, nombre):
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} es demasiado grande para un float finito") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero no booleano")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    for nombre, valor in (("base", base), ("tope", tope), ("fraccion", fraccion)):
        if not _es_numero(valor):
            raise ValueError(f"{nombre} debe ser int o float no booleano")

    b = _a_float_finito(base, "base")
    t = _a_float_finito(tope, "tope")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")
    f = _a_float_finito(fraccion, "fraccion")

    if intento >= _INTENTO_SATURACION:
        valor = t
    else:
        exacto = Fraction(b) * (1 << intento)
        valor = t if exacto >= Fraction(t) else float(exacto)

    return valor * f
