import math

# Con base >= 2**-1074 (menor float positivo) y tope < 2**1024, cualquier
# intento por encima de este umbral garantiza base * 2**intento > tope.
_INTENTO_SATURADO = 2200


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_magnitud(nombre, valor):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser int o float (no booleano)")
    try:
        como_float = float(valor)
    except OverflowError:
        raise ValueError(f"{nombre} no es representable como float finito") from None
    if not math.isfinite(como_float):
        raise ValueError(f"{nombre} debe ser finito")


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero (no booleano)")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_magnitud("base", base)
    _validar_magnitud("tope", tope)
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser int o float (no booleano)")
    if isinstance(fraccion, float) and not math.isfinite(fraccion):
        raise ValueError("fraccion debe ser finita")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento >= _INTENTO_SATURADO:
        # El crecimiento exponencial ya superó cualquier tope válido.
        limitado = tope
    elif isinstance(base, float):
        # Escalar por una potencia de dos es exacto salvo desborde, y un
        # desborde implica que se superó el tope (que es finito).
        try:
            limitado = min(tope, math.ldexp(base, intento))
        except OverflowError:
            limitado = tope
    else:
        # Entero exacto y acotado: intento < _INTENTO_SATURADO.
        limitado = min(tope, base << intento)

    return limitado * fraccion
