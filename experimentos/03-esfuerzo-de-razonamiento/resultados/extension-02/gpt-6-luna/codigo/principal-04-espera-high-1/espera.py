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
            or base_float <= 0 or tope_float < base_float
            or not 0 <= fraccion_float <= 1):
        raise ValueError("base, tope o fraccion inválidos")

    if base_float == tope_float:
        escalado = tope_float
    else:
        mantisa_base, exponente_base = math.frexp(base_float)
        mantisa_tope, exponente_tope = math.frexp(tope_float)
        exponente_escalado = exponente_base + intento
        if (exponente_escalado > exponente_tope
                or (exponente_escalado == exponente_tope
                    and mantisa_base >= mantisa_tope)):
            escalado = tope_float
        else:
            escalado = math.ldexp(base_float, intento)

    return escalado * fraccion_float
