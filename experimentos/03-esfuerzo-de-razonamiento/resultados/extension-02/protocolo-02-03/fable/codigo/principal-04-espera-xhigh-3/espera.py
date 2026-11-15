import math

# Todo float positivo es >= 2**-1074 y todo tope válido es < 2**1024, así que
# a partir de este intento base * 2**intento supera siempre al tope.
_INTENTO_DE_SATURACION = 1074 + 1024


def _es_numero_finito(valor):
    """Indica si valor es int/float (no bool) representable como float finito."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(float(valor))
    except OverflowError:
        return False


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    for nombre, valor in (("base", base), ("tope", tope), ("fraccion", fraccion)):
        if not _es_numero_finito(valor):
            raise ValueError(f"{nombre} debe ser un número int/float finito")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento >= _INTENTO_DE_SATURACION:
        limitada = tope
    elif isinstance(base, int):
        # Aritmética entera exacta; el exponente ya está acotado.
        limitada = min(tope, base * 2**intento)
    else:
        # ldexp escala de forma exacta sin convertir 2**intento a float.
        try:
            limitada = min(tope, math.ldexp(base, intento))
        except OverflowError:
            limitada = tope
    return limitada * fraccion
