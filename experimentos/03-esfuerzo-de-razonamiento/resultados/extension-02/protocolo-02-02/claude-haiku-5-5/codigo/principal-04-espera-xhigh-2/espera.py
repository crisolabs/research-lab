import math

# base >= 2**-1074, así que base * 2**2100 supera 2**1024 (desborda). 2200 deja margen.
_EXPONENTE_MAXIMO = 2200


def _real_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    base_f = _real_finito(base, "base")
    tope_f = _real_finito(tope, "tope")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    fraccion_f = _real_finito(fraccion, "fraccion")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    # ldexp multiplica por 2**k de forma exacta. Si desborda, base * 2**intento > tope.
    try:
        potencia = math.ldexp(base_f, min(intento, _EXPONENTE_MAXIMO))
    except OverflowError:
        potencia = tope_f
    return min(tope_f, potencia) * fraccion_f
