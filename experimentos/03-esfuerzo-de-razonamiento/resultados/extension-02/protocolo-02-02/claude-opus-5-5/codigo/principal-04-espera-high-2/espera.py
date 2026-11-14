import math


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _como_float_finito(valor):
    if not _es_numero(valor):
        raise ValueError("se esperaba un número int/float no booleano")
    try:
        convertido = float(valor)
    except (OverflowError, ValueError, TypeError):
        raise ValueError("el número no es representable como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError("el número debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero no booleano")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _como_float_finito(base)
    tope_f = _como_float_finito(tope)
    fraccion_f = _como_float_finito(fraccion)

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # tope < 2**1024 y base >= 2**-1074 (o >= 1 si es entero): por encima de
    # estos umbrales base * 2**intento supera seguro al tope.
    if isinstance(base, int):
        if intento > 1100:
            return tope * fraccion
        producto = base << intento
    else:
        if intento > 2200:
            return tope * fraccion
        try:
            producto = math.ldexp(base_f, intento)
        except OverflowError:
            return tope * fraccion
        if math.isinf(producto):
            return tope * fraccion

    return min(tope, producto) * fraccion
