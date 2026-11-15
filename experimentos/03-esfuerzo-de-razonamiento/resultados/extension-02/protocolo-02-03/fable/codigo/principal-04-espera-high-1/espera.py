import math

# Con base >= 2**-1074 (menor float positivo) y tope < 2**1024, a partir de
# este exponente base * 2**intento siempre alcanza o supera el tope.
_INTENTO_SATURADO = 2100


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _es_finito(valor):
    try:
        return math.isfinite(float(valor))
    except OverflowError:
        # Entero demasiado grande para representarse como float.
        return False


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not _es_numero(base) or not _es_finito(base):
        raise ValueError("base debe ser un número finito")
    if not _es_numero(tope) or not _es_finito(tope):
        raise ValueError("tope debe ser un número finito")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not _es_numero(fraccion) or not _es_finito(fraccion):
        raise ValueError("fraccion debe ser un número finito")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento >= _INTENTO_SATURADO:
        return tope * fraccion

    if isinstance(base, int):
        crecido = base << intento
    else:
        try:
            # Escalar por una potencia de dos es exacto salvo desborde.
            crecido = math.ldexp(base, intento)
        except OverflowError:
            # Supera cualquier float finito y, por lo tanto, el tope.
            return tope * fraccion

    return min(tope, crecido) * fraccion
