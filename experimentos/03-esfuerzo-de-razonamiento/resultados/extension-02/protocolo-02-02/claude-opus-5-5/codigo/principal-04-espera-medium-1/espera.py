import math

# base >= 2**-1074 (menor float positivo) y tope < 2**1024, así que con
# intentos mayores a este umbral el resultado siempre se satura en tope.
_UMBRAL_SATURACION = 2200


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _validar_finito(x, nombre):
    if not _es_numero(x):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        f = float(x)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float") from None
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")
    return f


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base_f = _validar_finito(base, "base")
    tope_f = _validar_finito(tope, "tope")
    _validar_finito(fraccion, "fraccion")

    if not (base_f > 0 and base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento > _UMBRAL_SATURACION:
        limitado = tope
    elif isinstance(base, int):
        # Entero acotado (a lo sumo ~3200 bits): cálculo exacto.
        limitado = min(tope, base * (1 << intento))
    else:
        try:
            valor = math.ldexp(base_f, intento)
        except OverflowError:
            limitado = tope
        else:
            limitado = min(tope, valor)

    return limitado * fraccion
