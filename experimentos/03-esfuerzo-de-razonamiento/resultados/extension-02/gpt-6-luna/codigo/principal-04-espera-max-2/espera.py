import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base, tope y fraccion deben ser números int o float")

    if not (base > 0 and base <= tope):
        raise ValueError("debe cumplirse 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    try:
        base_float = float(base)
        tope_float = float(tope)
        fraccion_float = float(fraccion)
    except (OverflowError, TypeError, ValueError):
        raise ValueError("base, tope y fraccion deben poder convertirse a float") from None

    if not (math.isfinite(base_float) and math.isfinite(tope_float)):
        raise ValueError("base y tope deben ser floats finitos")
    if not math.isfinite(fraccion_float):
        raise ValueError("fraccion debe ser finita")

    base_mantisa, base_exponente = math.frexp(base_float)
    tope_mantisa, tope_exponente = math.frexp(tope_float)
    exponente_escalado = base_exponente + intento

    if exponente_escalado > tope_exponente or (
        exponente_escalado == tope_exponente and base_mantisa > tope_mantisa
    ):
        escalado = tope_float
    else:
        escalado = math.ldexp(base_float, intento)

    return escalado * fraccion_float
