import math


def _real_finito(valor, nombre):
    """Valida un int/float no booleano representable como float finito."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no {type(valor).__name__}")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} es demasiado grande para representarse como float") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    """Devuelve min(tope, base * 2**intento) * fraccion sin desbordar."""
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    base_f = _real_finito(base, "base")
    tope_f = _real_finito(tope, "tope")
    fraccion_f = _real_finito(fraccion, "fraccion")

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    # Con base = mb * 2**eb y tope = mt * 2**et (0.5 <= mb, mt < 1):
    # si intento > et - eb, entonces base * 2**intento >= 2**et > tope.
    # Así nunca se calcula 2**intento, por grande que sea intento.
    _, exp_base = math.frexp(base_f)
    _, exp_tope = math.frexp(tope_f)
    if intento > exp_tope - exp_base:
        acotado = tope_f
    else:
        # Acá base * 2**intento < 2**et <= 2**1024: ldexp es exacto y finito.
        acotado = min(tope_f, math.ldexp(base_f, intento))
    return acotado * fraccion_f
