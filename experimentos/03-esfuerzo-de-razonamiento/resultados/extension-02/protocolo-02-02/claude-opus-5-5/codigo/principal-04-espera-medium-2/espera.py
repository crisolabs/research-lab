import math

# Con base >= 2**-1074 (mínimo float positivo) y tope < 2**1024,
# cualquier exponente >= 2100 hace que base * 2**intento supere al tope.
_EXP_MAX = 2100


def _numero_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        convertido = float(valor)
    except (OverflowError, ValueError):
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _numero_finito(base, "base")
    tope_f = _numero_finito(tope, "tope")
    fraccion_f = _numero_finito(fraccion, "fraccion")

    if not (0 < base and base <= tope and base_f > 0):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion_f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    n = min(intento, _EXP_MAX)
    if isinstance(base, int):
        crecido = base << n
    else:
        try:
            crecido = math.ldexp(base_f, n)
        except OverflowError:
            crecido = math.inf

    limitado = tope if crecido >= tope else crecido
    return limitado * fraccion
