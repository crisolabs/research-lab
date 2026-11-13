import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    def como_float(valor, nombre):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{nombre} debe ser un número int o float")
        try:
            resultado = float(valor)
        except (OverflowError, ValueError):
            raise ValueError(f"{nombre} debe poder representarse como float finito") from None
        if not math.isfinite(resultado):
            raise ValueError(f"{nombre} debe ser finito")
        return resultado

    base_float = como_float(base, "base")
    tope_float = como_float(tope, "tope")
    fraccion_float = como_float(fraccion, "fraccion")

    if base <= 0 or base > tope:
        raise ValueError("se requiere 0 < base <= tope")
    if fraccion < 0 or fraccion > 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    valor = base_float
    restantes = intento
    while restantes and valor < tope_float:
        # Comparar antes de duplicar evita el desbordamiento cerca del máximo float.
        if valor >= tope_float - valor:
            valor = tope_float
            break
        valor *= 2.0
        restantes -= 1

    return valor * fraccion_float
