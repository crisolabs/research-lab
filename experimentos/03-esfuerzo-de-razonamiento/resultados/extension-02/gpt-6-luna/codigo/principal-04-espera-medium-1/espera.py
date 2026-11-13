import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    def numero_finito(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            return None
        try:
            convertido = float(valor)
        except (OverflowError, ValueError):
            return None
        return convertido if math.isfinite(convertido) else None

    base_float = numero_finito(base)
    tope_float = numero_finito(tope)
    fraccion_float = numero_finito(fraccion)

    if (base_float is None or tope_float is None or fraccion_float is None
            or base_float <= 0 or tope_float <= 0 or base_float > tope_float
            or fraccion_float < 0 or fraccion_float > 1):
        raise ValueError("base, tope o fraccion fuera de rango")

    valor = base_float
    restantes = intento
    while restantes and valor < tope_float:
        if valor >= tope_float / 2:
            valor = tope_float
            break
        valor *= 2
        restantes -= 1

    return min(tope_float, valor) * fraccion_float
