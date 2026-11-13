import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("los parámetros deben ser números int o float")
        try:
            finito = math.isfinite(float(valor))
        except (OverflowError, ValueError):
            raise ValueError("los parámetros deben ser representables como float finito") from None
        if not finito:
            raise ValueError("los parámetros deben ser finitos")

    if not 0 < base <= tope or not 0 <= fraccion <= 1:
        raise ValueError("base, tope o fraccion fuera de rango")

    base = float(base)
    tope = float(tope)
    fraccion = float(fraccion)
    mantisa_base, exponente_base = math.frexp(base)
    mantisa_tope, exponente_tope = math.frexp(tope)
    diferencia = exponente_tope - exponente_base
    if intento > diferencia or (
        intento == diferencia and mantisa_base >= mantisa_tope
    ):
        return tope * fraccion
    return min(tope, math.ldexp(base, intento)) * fraccion
