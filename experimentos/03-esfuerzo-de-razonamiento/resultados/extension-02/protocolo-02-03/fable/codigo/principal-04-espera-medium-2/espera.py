import math
from fractions import Fraction

# Con base y tope representables como float finito y positivos, tope / base
# es menor que 2**2100; a partir de ese exponente siempre gana el tope.
_INTENTO_SATURADO = 2100


def _es_numero(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float):
        return math.isfinite(valor)
    try:
        float(valor)
    except OverflowError:
        return False
    return True


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not _es_numero(base) or not _es_numero(tope):
        raise ValueError("base y tope deben ser números finitos")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not _es_numero(fraccion) or not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe ser un número finito entre 0 y 1")

    if intento >= _INTENTO_SATURADO:
        limite = tope
    elif Fraction(base) * (1 << intento) >= Fraction(tope):
        # Comparación exacta, sin desbordes de float.
        limite = tope
    elif isinstance(base, float):
        # Menor que tope, así que es finito; ldexp escala de forma exacta.
        limite = math.ldexp(base, intento)
    else:
        limite = base << intento

    return limite * fraccion
