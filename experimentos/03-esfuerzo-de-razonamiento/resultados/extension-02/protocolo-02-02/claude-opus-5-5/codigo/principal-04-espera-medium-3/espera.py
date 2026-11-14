import math

# Con base >= 2**-1074 (mínimo float positivo) y tope < 2**1024, cualquier
# intento >= 2099 hace que base * 2**intento supere al tope.
_UMBRAL_INTENTO = 2200


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _validar_finito(x, nombre):
    if not _es_numero(x):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        valor = float(x)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito")
    return valor


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _validar_finito(base, "base")
    tope_f = _validar_finito(tope, "tope")
    if not (0 < base_f <= tope_f) or not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser int o float")
    if isinstance(fraccion, int):
        if not (0 <= fraccion <= 1):
            raise ValueError("fraccion debe estar entre 0 y 1")
    else:
        if not math.isfinite(fraccion) or not (0.0 <= fraccion <= 1.0):
            raise ValueError("fraccion debe ser finita y estar entre 0 y 1")

    if intento >= _UMBRAL_INTENTO:
        limitado = tope
    else:
        if isinstance(base, int):
            producto = base * (1 << intento)
        else:
            try:
                producto = math.ldexp(base, intento)
            except OverflowError:
                producto = math.inf
        limitado = tope if producto >= tope else producto

    return limitado * fraccion
