import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for nombre, valor in (("base", base), ("tope", tope), ("fraccion", fraccion)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{nombre} debe ser un int o float finito")
        try:
            finito = math.isfinite(valor)
        except OverflowError:
            finito = False
        if not finito:
            raise ValueError(f"{nombre} debe poder representarse como float finito")

    if not 0 < base <= tope:
        raise ValueError("base y tope deben cumplir 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    exponente_base = math.frexp(base)[1]
    exponente_tope = math.frexp(tope)[1]
    if intento > exponente_tope - exponente_base:
        return tope * fraccion

    if isinstance(base, int):
        valor = base << intento
    else:
        valor = math.ldexp(base, intento)
    return min(tope, valor) * fraccion
