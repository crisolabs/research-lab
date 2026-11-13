import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base, tope y fraccion deben ser números")

    if not 0 < base <= tope or not 0 <= fraccion <= 1:
        raise ValueError("base, tope o fraccion fuera de rango")

    try:
        base, tope, fraccion = float(base), float(tope), float(fraccion)
    except (OverflowError, ValueError) as error:
        raise ValueError("los parámetros deben representarse como float finitos") from error

    if not all(math.isfinite(valor) for valor in (base, tope, fraccion)):
        raise ValueError("los parámetros deben ser finitos")

    exponente_base = math.frexp(base)[1]
    exponente_tope = math.frexp(tope)[1]
    if intento > exponente_tope - exponente_base:
        demora = tope
    else:
        demora = min(tope, math.ldexp(base, intento))
    return demora * fraccion
