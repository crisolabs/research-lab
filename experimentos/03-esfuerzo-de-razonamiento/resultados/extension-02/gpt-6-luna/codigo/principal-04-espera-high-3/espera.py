import math


def _numero_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("el valor debe ser un int o float finito, no booleano")
    try:
        convertido = float(valor)
    except (OverflowError, TypeError, ValueError):
        raise ValueError("el valor debe poder representarse como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError("el valor debe poder representarse como float finito")
    return convertido


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo, no booleano")

    base_float = _numero_finito(base)
    tope_float = _numero_finito(tope)
    fraccion_float = _numero_finito(fraccion)

    if base <= 0 or tope <= 0 or base > tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion_float <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    if base_float >= tope_float or intento == 0:
        espera_base = base_float
    else:
        try:
            espera_base = math.ldexp(base_float, intento)
        except OverflowError:
            espera_base = tope_float
    return min(tope_float, espera_base) * fraccion_float
