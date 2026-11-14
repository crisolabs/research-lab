import math


def _real_finito(valor, nombre):
    """Valida un int/float no booleano y finito; lo devuelve como float."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no {type(valor).__name__}")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito")
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero no booleano")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base = _real_finito(base, "base")
    tope = _real_finito(tope, "tope")
    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")

    fraccion = _real_finito(fraccion, "fraccion")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1")

    # base >= tiny positivo y 2**1024 supera a cualquier float finito,
    # así que para intentos >= 1024 el mínimo es siempre el tope.
    if intento >= 1024:
        exponencial = tope
    else:
        # Puede desbordar a inf para valores grandes; min() lo resuelve con tope.
        exponencial = base * float(2 ** intento)
        exponencial = min(tope, exponencial)
    return min(tope, exponencial) * fraccion
