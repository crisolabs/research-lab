import math

# Con base y tope representables como float finito y positivos, tope / base
# es menor que 2**1024 / 2**-1074 = 2**2098. A partir de este exponente el
# tope siempre gana, así que no hace falta calcular la potencia.
_INTENTO_SATURADO = 2200


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_finito(valor, nombre):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser int o float (no booleano)")
    if isinstance(valor, float):
        if not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito")
    else:
        try:
            float(valor)
        except OverflowError:
            raise ValueError(
                f"{nombre} es demasiado grande para representarse como float"
            ) from None


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero (no booleano)")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    _validar_finito(base, "base")
    _validar_finito(tope, "tope")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser int o float (no booleano)")
    # La comparación también descarta NaN e infinitos.
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento >= _INTENTO_SATURADO:
        return tope * fraccion

    if isinstance(base, float):
        try:
            crecido = math.ldexp(base, intento)
        except OverflowError:
            return tope * fraccion
    else:
        crecido = base << intento

    return min(tope, crecido) * fraccion
