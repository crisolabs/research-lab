import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    valores = (base, tope, fraccion)
    if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
        raise ValueError("base, tope y fraccion deben ser números int o float")

    try:
        base_float, tope_float, fraccion_float = (float(valor) for valor in valores)
    except (OverflowError, ValueError):
        raise ValueError("los parámetros deben poder representarse como float finito") from None

    if not all(math.isfinite(valor) for valor in (base_float, tope_float, fraccion_float)):
        raise ValueError("los parámetros deben ser finitos")
    if not (0 < base_float <= tope_float):
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion_float <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    valor = base_float
    for _ in range(intento):
        if valor >= tope_float / 2:
            valor = tope_float
            break
        valor *= 2
        if valor >= tope_float:
            valor = tope_float
            break

    return valor * fraccion_float
