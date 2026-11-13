import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    valores = []
    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("los parámetros deben ser números finitos")
        try:
            convertido = float(valor)
        except (OverflowError, ValueError):
            raise ValueError("los parámetros deben ser números finitos") from None
        if not math.isfinite(convertido):
            raise ValueError("los parámetros deben ser números finitos")
        valores.append(convertido)

    if not 0 < base <= tope or not 0 <= fraccion <= 1:
        raise ValueError("base, tope o fraccion fuera de rango")

    base, tope, fraccion = valores
    exponente_base = math.frexp(base)[1]
    exponente_tope = math.frexp(tope)[1]
    if intento > exponente_tope - exponente_base:
        limite = tope
    else:
        try:
            limite = min(tope, math.ldexp(base, intento))
        except OverflowError:
            limite = tope
    return limite * fraccion
