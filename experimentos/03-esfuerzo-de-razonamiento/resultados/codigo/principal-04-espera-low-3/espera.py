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

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")
    base, tope, fraccion = valores

    limite = math.frexp(tope)[1] - math.frexp(base)[1]
    if intento > limite:
        return tope * fraccion
    try:
        escalado = math.ldexp(base, intento)
    except OverflowError:
        escalado = tope
    return min(tope, escalado) * fraccion
