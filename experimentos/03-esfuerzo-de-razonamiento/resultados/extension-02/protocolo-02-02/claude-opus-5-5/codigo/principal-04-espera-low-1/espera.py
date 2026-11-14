import math


def _numero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        f = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no representable como float") from None
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")
    return f


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    b = _numero(base, "base")
    t = _numero(tope, "tope")
    f = _numero(fraccion, "fraccion")
    if not (0 < b <= t):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento >= 2200:
        valor = t
    else:
        try:
            valor = min(t, math.ldexp(b, intento))
        except OverflowError:
            valor = t
    return valor * f
