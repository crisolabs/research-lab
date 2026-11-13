import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base, tope y fraccion deben ser números finitos")
        try:
            finito = math.isfinite(valor)
        except OverflowError:
            raise ValueError("base, tope y fraccion deben ser números finitos") from None
        if not finito:
            raise ValueError("base, tope y fraccion deben ser números finitos")

    if not 0 < base <= tope:
        raise ValueError("base y tope deben cumplir 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    if isinstance(base, int):
        if intento >= math.frexp(tope)[1]:
            valor = tope
        else:
            valor = base << intento
    else:
        try:
            valor = math.ldexp(base, intento)
        except OverflowError:
            valor = tope

    return min(tope, valor) * fraccion
