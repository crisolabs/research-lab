import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    def numero_finito(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("el parámetro debe ser un número int o float")
        try:
            convertido = float(valor)
        except (OverflowError, ValueError):
            raise ValueError("el parámetro debe poder representarse como float") from None
        if not math.isfinite(convertido):
            raise ValueError("el parámetro debe ser finito")
        return convertido

    base_float = numero_finito(base)
    tope_float = numero_finito(tope)
    fraccion_float = numero_finito(fraccion)

    if base <= 0 or tope <= 0 or base > tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    base_mantisa, base_exponente = math.frexp(base_float)
    tope_mantisa, tope_exponente = math.frexp(tope_float)
    exponente_resultado = base_exponente + intento

    if (exponente_resultado > tope_exponente or
            (exponente_resultado == tope_exponente and
             base_mantisa >= tope_mantisa)):
        limitado = tope_float
    else:
        limitado = math.ldexp(base_float, intento)

    return limitado * fraccion_float
