import math
import sys

# Todo float finito (y todo entero convertible a float finito) es < 2**_EXP_MAX.
_EXP_MAX = sys.float_info.max_exp


def _es_real_finito(valor):
    """Indica si `valor` es int/float (no bool) representable como float finito."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(float(valor))
    except OverflowError:
        return False


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not _es_real_finito(base) or not _es_real_finito(tope):
        raise ValueError("base y tope deben ser números finitos representables como float")
    if not 0 < base <= tope:
        raise ValueError("debe cumplirse 0 < base <= tope")
    if not _es_real_finito(fraccion) or not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe ser un número finito entre 0 y 1")

    # Se calcula base * 2**intento sólo cuando el resultado es acotado; si el
    # exponente ya garantiza que supera al tope, se usa el tope directamente.
    if isinstance(base, int):
        # base >= 1, por lo que base * 2**intento >= 2**intento.
        if intento >= _EXP_MAX:
            return tope * fraccion
        producto = base << intento
    else:
        # base = m * 2**exponente con 0.5 <= m < 1.
        _, exponente = math.frexp(base)
        if intento > _EXP_MAX - exponente:
            return tope * fraccion
        producto = math.ldexp(base, intento)

    return min(tope, producto) * fraccion
