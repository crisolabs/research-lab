import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("los parámetros deben ser números finitos")
        try:
            finito = math.isfinite(valor)
        except OverflowError:
            raise ValueError("el número no se puede representar como float finito") from None
        if not finito:
            raise ValueError("los parámetros deben ser números finitos")

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    base = float(base)
    tope = float(tope)
    mantisa_base, exponente_base = math.frexp(base)
    mantisa_tope, exponente_tope = math.frexp(tope)
    diferencia = exponente_tope - exponente_base
    if intento > diferencia or (
        intento == diferencia and mantisa_base >= mantisa_tope
    ):
        return tope * fraccion
    return math.ldexp(base, intento) * fraccion
