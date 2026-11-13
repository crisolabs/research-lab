from math import frexp, isfinite, ldexp


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for nombre, valor in (("base", base), ("tope", tope), ("fraccion", fraccion)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{nombre} debe ser un número int/float finito")
        try:
            finito = isfinite(valor)
        except OverflowError:
            finito = False
        if not finito:
            raise ValueError(f"{nombre} debe poder representarse como un float finito")

    if not 0 < base <= tope:
        raise ValueError("base y tope deben cumplir 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    limite = frexp(tope)[1] - frexp(base)[1] + 1
    if intento > limite:
        return tope * fraccion

    if isinstance(base, int):
        demora = base << intento
    else:
        try:
            demora = ldexp(base, intento)
        except OverflowError:
            demora = tope

    return min(tope, demora) * fraccion
