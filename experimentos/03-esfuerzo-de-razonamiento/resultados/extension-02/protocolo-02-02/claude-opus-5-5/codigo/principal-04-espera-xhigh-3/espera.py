import math

# Cualquier base positiva representable como float es >= 2**-1074 y cualquier
# tope representable es < 2**1024; por lo tanto, para intento >= 2098 el
# producto base * 2**intento siempre supera al tope.
_UMBRAL_INTENTO = 2100


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_positivo_finito(valor, nombre):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser un número int o float")
    try:
        como_float = float(valor)
    except (OverflowError, ValueError, TypeError):
        raise ValueError(f"{nombre} debe poder representarse como float finito") from None
    if not math.isfinite(como_float):
        raise ValueError(f"{nombre} debe ser finito")
    if not valor > 0:
        raise ValueError(f"{nombre} debe ser positivo")


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_positivo_finito(base, "base")
    _validar_positivo_finito(tope, "tope")
    if not base <= tope:
        raise ValueError("base debe ser menor o igual que tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser un número int o float")
    if isinstance(fraccion, float) and not math.isfinite(fraccion):
        raise ValueError("fraccion debe ser finita")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento >= _UMBRAL_INTENTO:
        valor = tope
    else:
        if isinstance(base, int):
            producto = base * (1 << intento)
        else:
            try:
                producto = math.ldexp(base, intento)
            except OverflowError:
                producto = math.inf
        valor = min(tope, producto)

    return valor * fraccion
