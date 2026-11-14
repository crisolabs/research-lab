import math

_EXPONENTE_MAX = 2200


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _como_float_finito(valor, nombre):
    try:
        resultado = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no cabe en un float") from None
    if not math.isfinite(resultado):
        raise ValueError(f"{nombre} debe ser finito")
    return resultado


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not (_es_numero(base) and _es_numero(tope) and _es_numero(fraccion)):
        raise ValueError("base, tope y fraccion deben ser int o float, no booleanos")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    base = _como_float_finito(base, "base")
    tope = _como_float_finito(tope, "tope")

    # Desde intento 2200 el resultado ya es tope: base >= 2**-1074 y
    # 2**2200 * 2**-1074 supera al mayor float. Se satura el exponente para
    # no construir 2**intento.
    try:
        crecido = math.ldexp(base, min(intento, _EXPONENTE_MAX))
    except OverflowError:
        crecido = math.inf
    return min(tope, crecido) * float(fraccion)
