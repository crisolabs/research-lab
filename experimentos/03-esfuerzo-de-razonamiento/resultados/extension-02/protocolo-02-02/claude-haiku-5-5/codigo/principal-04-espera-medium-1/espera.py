import math


def _real(valor, nombre):
    """Valida un int/float finito (no booleano) y lo devuelve como float."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no {type(valor).__name__}")
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
        raise ValueError("intento debe ser no negativo")

    base = _real(base, "base")
    tope = _real(tope, "tope")
    fraccion = _real(fraccion, "fraccion")

    if not (0.0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0.0 <= fraccion <= 1.0):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # Comparación exacta de min(tope, base * 2**intento) sin construir
    # potencias gigantes ni desbordar: se usa la descomposición
    # base = mb * 2**eb y tope = mt * 2**et con 0.5 <= mb, mt < 1.
    mb, eb = math.frexp(base)
    mt, et = math.frexp(tope)
    exponente = eb + intento

    if exponente > et:
        # base * 2**intento >= 2**(exponente - 1) >= 2**et > tope
        limitado = tope
    elif exponente < et:
        # base * 2**intento < 2**exponente <= 2**(et - 1) <= tope
        limitado = math.ldexp(base, intento)
    elif mb < mt:
        limitado = math.ldexp(base, intento)
    else:
        limitado = tope

    return limitado * fraccion
