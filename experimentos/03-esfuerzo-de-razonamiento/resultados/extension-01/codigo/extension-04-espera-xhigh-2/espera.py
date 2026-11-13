import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    valores = (base, tope, fraccion)
    if any(isinstance(valor, bool) or not isinstance(valor, (int, float))
           for valor in valores):
        raise ValueError("base, tope y fraccion deben ser int o float")

    try:
        base_float, tope_float, fraccion_float = map(float, valores)
    except (OverflowError, ValueError):
        raise ValueError("los valores deben poder representarse como float finitos") from None

    if not all(math.isfinite(valor)
               for valor in (base_float, tope_float, fraccion_float)):
        raise ValueError("base, tope y fraccion deben ser finitos")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    _, exponente_base = math.frexp(base_float)
    _, exponente_tope = math.frexp(tope_float)
    diferencia = exponente_tope - exponente_base
    if intento > diferencia:
        espera_limitada = tope
    elif isinstance(base, int):
        espera_limitada = min(tope, base << intento)
    else:
        espera_limitada = min(tope, math.ldexp(base_float, intento))

    return espera_limitada * fraccion
