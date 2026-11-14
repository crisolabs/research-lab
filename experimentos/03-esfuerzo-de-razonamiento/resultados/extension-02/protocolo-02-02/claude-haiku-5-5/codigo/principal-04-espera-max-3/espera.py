import math


def _validar_real(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    try:
        real = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no se puede representar como float") from None
    if not math.isfinite(real):
        raise ValueError(f"{nombre} debe ser finito")
    return real


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    base_real = _validar_real(base, "base")
    tope_real = _validar_real(tope, "tope")
    fraccion_real = _validar_real(fraccion, "fraccion")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion_real <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    # Se decide base * 2**intento >= tope comparando (exponente, mantisa) en
    # base 2, sin calcular la potencia (podría ser un entero enorme).
    mantisa_base, exp_base = math.frexp(base_real)
    mantisa_tope, exp_tope = math.frexp(tope_real)
    if (exp_base + intento, mantisa_base) >= (exp_tope, mantisa_tope):
        crecido = tope_real
    else:
        # Acá base * 2**intento < tope: el escalado es exacto y no desborda.
        crecido = math.ldexp(base_real, intento)
    return crecido * fraccion_real
