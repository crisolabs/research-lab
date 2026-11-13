import math
import sys


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    for valor in (base, tope):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError("base y tope deben ser números finitos")
        try:
            representable = math.isfinite(float(valor))
        except (OverflowError, TypeError, ValueError):
            representable = False
        if not representable:
            raise ValueError("base y tope deben ser números finitos")

    if base <= 0 or tope <= 0 or base > tope:
        raise ValueError("se requiere 0 < base <= tope")

    if isinstance(fraccion, bool) or not isinstance(fraccion, (int, float)):
        raise ValueError("fraccion debe ser un número entre 0 y 1")
    if isinstance(fraccion, float) and not math.isfinite(fraccion):
        raise ValueError("fraccion debe ser finita")
    if fraccion < 0 or fraccion > 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    valor = tope if base == tope else base
    for _ in range(intento):
        if valor >= tope:
            valor = tope
            break

        if isinstance(valor, float) and valor > sys.float_info.max / 2:
            valor = tope
            break
        duplicado = valor * 2
        if duplicado >= tope:
            valor = tope
            break
        valor = duplicado

    return valor * fraccion
