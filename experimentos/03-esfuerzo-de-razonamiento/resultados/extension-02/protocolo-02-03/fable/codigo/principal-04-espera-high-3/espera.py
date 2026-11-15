import math

# Con base y tope representables como float finito y 0 < base <= tope, vale
# tope / base < 2**1024 / 2**-1074 = 2**2098. A partir de ese exponente,
# base * 2**intento supera siempre a tope y no hace falta calcularlo.
_EXPONENTE_SATURACION = 2098


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_magnitud(nombre, valor):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser un número int o float")
    try:
        finito = math.isfinite(float(valor))
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError(f"{nombre} debe poder representarse como float finito")


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    _validar_magnitud("base", base)
    _validar_magnitud("tope", tope)
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser un número int o float")
    if not 0 <= fraccion <= 1:  # también descarta NaN e infinitos
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento >= _EXPONENTE_SATURACION:
        limitado = tope
    else:
        if isinstance(base, float):
            try:
                crecido = math.ldexp(base, intento)
            except OverflowError:
                crecido = math.inf
        else:
            crecido = base << intento
        limitado = min(tope, crecido)

    return limitado * fraccion
