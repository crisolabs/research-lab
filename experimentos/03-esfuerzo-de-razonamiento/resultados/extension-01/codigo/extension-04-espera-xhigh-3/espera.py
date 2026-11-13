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
            raise ValueError(f"{nombre} debe poder representarse como float finito") from None
        if not finito:
            raise ValueError(f"{nombre} debe ser finito")

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    diferencia = math.frexp(tope)[1] - math.frexp(base)[1]
    if intento > diferencia:
        demora = tope
    elif isinstance(base, int):
        demora = min(tope, base << intento)
    else:
        demora = min(tope, math.ldexp(base, intento))
    return demora * fraccion
