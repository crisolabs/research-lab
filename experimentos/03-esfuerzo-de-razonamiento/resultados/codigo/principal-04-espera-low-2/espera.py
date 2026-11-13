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
        except (OverflowError, ValueError) as error:
            raise ValueError("los parámetros deben ser números finitos") from error
        if not math.isfinite(convertido):
            raise ValueError("los parámetros deben ser números finitos")
        valores.append(convertido)

    base, tope, fraccion = valores
    if not 0 < base <= tope or not 0 <= fraccion <= 1:
        raise ValueError("los parámetros están fuera de rango")

    if intento >= 2098:
        demora = tope
    else:
        try:
            demora = min(tope, math.ldexp(base, intento))
        except OverflowError:
            demora = tope
    return demora * fraccion
