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
            raise ValueError("el valor debe poder representarse como float finito") from None
        if not finito:
            raise ValueError("base, tope y fraccion deben ser números finitos")

    if not 0 < base <= tope:
        raise ValueError("debe cumplirse 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    exponente_base = base.bit_length() if isinstance(base, int) else math.frexp(base)[1]
    exponente_tope = math.frexp(tope)[1]
    if intento > exponente_tope - exponente_base:
        return tope * fraccion

    escalada = base << intento if isinstance(base, int) else math.ldexp(base, intento)
    return min(tope, escalada) * fraccion
