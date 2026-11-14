import math

# Con base >= 2**-1074 (mínimo float positivo) y tope < 2**1024, cualquier
# intento mayor a este umbral garantiza base * 2**intento > tope.
_UMBRAL_INTENTO = 2200


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _validar_finito(x, nombre):
    if not _es_numero(x):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")
    try:
        f = float(x)
    except (OverflowError, ValueError, TypeError):
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero no booleano")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_finito(base, "base")
    _validar_finito(tope, "tope")
    _validar_finito(fraccion, "fraccion")

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento > _UMBRAL_INTENTO:
        limitado = tope
    else:
        if isinstance(base, int):
            valor = base << intento
        else:
            try:
                valor = math.ldexp(base, intento)
            except OverflowError:
                valor = math.inf
        limitado = min(tope, valor)

    return limitado * fraccion
