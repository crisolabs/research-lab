import math

# Con base >= 2**-1074 y tope < 2**1024, base * 2**intento supera cualquier
# tope válido cuando intento pasa este límite.
_INTENTO_SATURADO = 2200


def _numero_finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float")
    if isinstance(valor, float):
        if not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito")
    else:
        try:
            float(valor)
        except OverflowError:
            raise ValueError(f"{nombre} no es representable como float") from None


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")
    _numero_finito(base, "base")
    _numero_finito(tope, "tope")
    _numero_finito(fraccion, "fraccion")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1")

    if intento > _INTENTO_SATURADO:
        limite = tope
    else:
        try:
            if isinstance(base, float):
                crecido = math.ldexp(base, intento)  # exacto
            else:
                crecido = base * 2 ** intento  # entero acotado
        except OverflowError:
            limite = tope
        else:
            limite = min(tope, crecido)
    return limite * fraccion
