import math


def _real_finito(valor, nombre):
    """Valida un int/float no booleano y finito, y lo devuelve como float."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no booleano")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    """Calcula min(tope, base * 2**intento) * fraccion sin azar interno.

    Evita construir 2**intento: la comparación con tope se hace con
    frexp (mantisa y exponente), y ldexp sólo se usa cuando el resultado
    es menor o igual que tope, por lo que no puede desbordar.
    """
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser int, no booleano")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    b = _real_finito(base, "base")
    t = _real_finito(tope, "tope")
    f = _real_finito(fraccion, "fraccion")

    if not (0.0 < b <= t):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0.0 <= f <= 1.0):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # b = mb * 2**eb y t = mt * 2**et, con mb y mt en [0.5, 1).
    # base * 2**intento = mb * 2**(eb + intento); su relación con tope
    # depende de d = (eb + intento) - et y de las mantisas.
    mb, eb = math.frexp(b)
    mt, et = math.frexp(t)
    d = (eb + intento) - et

    if d >= 2:
        supera = True
    elif d <= -2:
        supera = False
    else:
        # Aquí d es pequeño, así que ldexp es exacto y acotado.
        supera = math.ldexp(mb, d) > mt

    if supera:
        valor = t
    else:
        # base * 2**intento <= tope <= float máximo: no desborda.
        valor = math.ldexp(b, intento)

    return valor * f
