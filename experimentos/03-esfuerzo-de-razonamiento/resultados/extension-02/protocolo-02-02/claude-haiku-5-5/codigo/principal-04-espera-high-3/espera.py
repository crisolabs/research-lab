import math


def _numero(valor, nombre):
    """Valida un int/float no booleano y finito. Devuelve (valor original, valor float)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")
    try:
        valor_float = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(valor_float):
        raise ValueError(f"{nombre} debe ser finito")
    return valor, valor_float


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    base_raw, base_f = _numero(base, "base")
    tope_raw, tope_f = _numero(tope, "tope")
    if not (0 < base_raw <= tope_raw):
        raise ValueError("se requiere 0 < base <= tope")

    fraccion_raw, fraccion_f = _numero(fraccion, "fraccion")
    if not (0 <= fraccion_raw <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base * 2**intento = m * 2**ex, con 0.5 <= m < 1 (sin construir 2**intento).
    m, e = math.frexp(base_f)
    _, et = math.frexp(tope_f)
    ex = e + intento

    if ex > et + 1:
        # base * 2**intento >= 2**(et+1) > tope
        valor = tope_f
    else:
        try:
            valor = min(tope_f, math.ldexp(m, ex))
        except OverflowError:
            # Desbordaría el float, por lo tanto es mayor que tope
            valor = tope_f

    return valor * fraccion_f
