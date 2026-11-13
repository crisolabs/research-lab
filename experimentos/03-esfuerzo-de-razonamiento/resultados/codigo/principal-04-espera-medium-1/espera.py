import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base, tope y fraccion deben ser números finitos")
        try:
            finito = math.isfinite(float(valor))
        except OverflowError:
            raise ValueError("el número debe poder representarse como float finito") from None
        if not finito:
            raise ValueError("base, tope y fraccion deben ser números finitos")

    if not 0 < base <= tope or not 0 <= fraccion <= 1:
        raise ValueError("se requiere 0 < base <= tope y 0 <= fraccion <= 1")

    base, tope, fraccion = float(base), float(tope), float(fraccion)
    mantisa_base, exponente_base = math.frexp(base)
    mantisa_tope, exponente_tope = math.frexp(tope)
    diferencia = exponente_tope - exponente_base
    if intento > diferencia or (
        intento == diferencia and mantisa_base >= mantisa_tope
    ):
        return tope * fraccion
    return math.ldexp(base, intento) * fraccion
