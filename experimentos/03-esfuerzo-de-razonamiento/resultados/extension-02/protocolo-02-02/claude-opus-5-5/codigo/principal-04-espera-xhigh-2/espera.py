import math
from fractions import Fraction

# Todo tope válido es un float finito, por lo que tope < 2**1024. La base
# positiva más chica posible es 2**-1074 (float subnormal mínimo). Entonces,
# para intento >= 1024 + 1074, base * 2**intento >= 2**1024 > tope siempre.
_UMBRAL_INTENTO = 1024 + 1074


def _es_numero_real(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_finito_float(valor, nombre):
    if not _es_numero_real(valor):
        raise ValueError(f"{nombre} debe ser int o float (no booleano)")
    try:
        convertido = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser finito")


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero (no booleano)")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_finito_float(base, "base")
    _validar_finito_float(tope, "tope")
    _validar_finito_float(fraccion, "fraccion")

    if not (0 < base <= tope):
        raise ValueError("se requiere 0 < base <= tope")
    if not (0 <= fraccion <= 1):
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    # min(tope, x) devuelve tope salvo que x < tope.
    if intento >= _UMBRAL_INTENTO:
        limitado = tope
    else:
        # Comparación exacta; el exponente está acotado, así que el entero
        # intermedio es de tamaño moderado.
        exacto = Fraction(base) * (1 << intento)
        if exacto < tope:
            if isinstance(base, int):
                limitado = base << intento
            else:
                # Exacto: el resultado es menor que tope, por ende representable.
                limitado = math.ldexp(base, intento)
        else:
            limitado = tope

    return limitado * fraccion
