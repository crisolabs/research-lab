import math

# Cota de intentos a partir de la cual base * 2**intento supera siempre a
# cualquier tope finito representable como float (base >= menor subnormal).
_INTENTO_SATURACION = 2200


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _como_float_finito(valor, nombre):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        convertido = float(valor)
    except (OverflowError, ValueError):
        raise ValueError(f"{nombre} no es representable como float") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _como_float_finito(base, "base")
    _como_float_finito(tope, "tope")
    fraccion_f = _como_float_finito(fraccion, "fraccion")

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion_f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento >= _INTENTO_SATURACION:
        limitado = tope
    else:
        if isinstance(base, int):
            producto = base << intento
        else:
            try:
                producto = math.ldexp(base, intento)
            except OverflowError:
                producto = math.inf
        limitado = tope if producto >= tope else producto

    return limitado * fraccion
