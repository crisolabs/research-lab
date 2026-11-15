import math

# Con base >= 5e-324 (mínimo float positivo) y tope < 2**1024, cualquier
# intento mayor que este límite satura siempre en el tope.
_INTENTO_SATURA = 2200


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _validar_finito(x, nombre):
    if not _es_numero(x):
        raise ValueError(f"{nombre} debe ser int o float (no booleano)")
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError(f"{nombre} debe ser finito")
    else:
        try:
            float(x)
        except OverflowError:
            raise ValueError(
                f"{nombre} es demasiado grande para representarse como float"
            ) from None


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero (no booleano)")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_finito(base, "base")
    _validar_finito(tope, "tope")
    _validar_finito(fraccion, "fraccion")

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento > _INTENTO_SATURA:
        limitado = tope
    elif isinstance(base, float):
        try:
            limitado = min(tope, math.ldexp(base, intento))
        except OverflowError:
            limitado = tope
    else:
        limitado = min(tope, base << intento)

    return limitado * fraccion
