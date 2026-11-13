import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")

    def como_float_finito(valor, nombre):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{nombre} debe ser un número int o float finito")
        try:
            convertido = float(valor)
        except (OverflowError, TypeError, ValueError):
            raise ValueError(f"{nombre} debe poder representarse como un float finito") from None
        if not math.isfinite(convertido):
            raise ValueError(f"{nombre} debe poder representarse como un float finito")
        return convertido

    base_float = como_float_finito(base, "base")
    tope_float = como_float_finito(tope, "tope")
    fraccion_float = como_float_finito(fraccion, "fraccion")

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    valor = base_float
    restante = intento
    while restante > 0 and valor < tope_float:
        duplicado = valor * 2.0
        if not math.isfinite(duplicado) or duplicado >= tope_float:
            valor = tope_float
            break
        valor = duplicado
        restante -= 1

    return valor * fraccion_float
