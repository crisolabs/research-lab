import math

# 2**2098 supera tope/base para cualquier par de floats válidos, así que desde
# ese exponente en adelante min(tope, base * 2**intento) siempre vale tope.
_EXPONENTE_MAXIMO = 2100


def _real_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        flotante = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(flotante):
        raise ValueError(f"{nombre} debe ser finito")
    return flotante


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    b = _real_finito(base, "base")
    t = _real_finito(tope, "tope")
    f = _real_finito(fraccion, "fraccion")

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    try:
        escalado = math.ldexp(b, min(intento, _EXPONENTE_MAXIMO))
    except OverflowError:
        escalado = math.inf

    return min(t, escalado) * f
