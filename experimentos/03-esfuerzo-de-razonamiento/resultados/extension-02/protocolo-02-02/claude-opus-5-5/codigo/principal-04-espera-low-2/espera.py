import math


def _numero_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        f = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float") from None
    if not math.isfinite(f):
        raise ValueError(f"{nombre} debe ser finito")
    return f


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    b = _numero_finito(base, "base")
    t = _numero_finito(tope, "tope")
    f = _numero_finito(fraccion, "fraccion")
    if not (0 < b <= t):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= f <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # Duplicar en float es exacto; se alcanza el tope en a lo sumo ~2100 pasos.
    v = b
    i = 0
    while i < intento and v < t:
        v *= 2
        i += 1
    return min(t, v) * f
