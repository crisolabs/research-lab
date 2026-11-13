import math
import sys


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope, fraccion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base, tope y fraccion deben ser números int o float")

    try:
        base_float = float(base)
        tope_float = float(tope)
    except (OverflowError, TypeError, ValueError):
        raise ValueError("base y tope deben poder representarse como floats finitos") from None

    if not math.isfinite(base_float) or not math.isfinite(tope_float):
        raise ValueError("base y tope deben poder representarse como floats finitos")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    valor = base
    duplicaciones = 0
    mitad_max_float = sys.float_info.max / 2

    while duplicaciones < intento and valor < tope:
        if isinstance(valor, float) and valor > mitad_max_float:
            valor = tope
            break

        duplicado = valor * 2
        if duplicado >= tope:
            valor = tope
            break

        valor = duplicado
        duplicaciones += 1

    return valor * fraccion
