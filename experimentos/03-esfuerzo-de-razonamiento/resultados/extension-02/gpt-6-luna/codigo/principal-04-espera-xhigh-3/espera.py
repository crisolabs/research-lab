import math


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    intento = int(intento)

    def normalizar_numero(valor, nombre):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"{nombre} debe ser int o float")
        return int(valor) if isinstance(valor, int) else float(valor)

    base = normalizar_numero(base, "base")
    tope = normalizar_numero(tope, "tope")
    fraccion = normalizar_numero(fraccion, "fraccion")

    try:
        base_finita = math.isfinite(float(base))
        tope_finito = math.isfinite(float(tope))
    except (OverflowError, TypeError, ValueError):
        raise ValueError("base y tope deben poder representarse como floats finitos") from None
    if not base_finita or not tope_finito:
        raise ValueError("base y tope deben poder representarse como floats finitos")

    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if isinstance(fraccion, float) and not math.isfinite(fraccion):
        raise ValueError("fraccion debe ser finita y estar entre 0 y 1")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe ser finita y estar entre 0 y 1")

    def razon_exacta(valor):
        if isinstance(valor, int):
            return valor, 1
        return valor.as_integer_ratio()

    base_num, base_den = razon_exacta(base)
    tope_num, tope_den = razon_exacta(tope)
    izquierda = base_num * tope_den
    derecha = tope_num * base_den

    # Compara base * 2**intento con tope sin construir 2**intento.
    bits_izquierda = izquierda.bit_length() + intento
    bits_derecha = derecha.bit_length()
    if bits_izquierda > bits_derecha:
        alcanza_tope = True
    elif bits_izquierda < bits_derecha:
        alcanza_tope = False
    else:
        alcanza_tope = (izquierda << intento) >= derecha

    if alcanza_tope:
        escalado = tope
    elif isinstance(base, int):
        escalado = base << intento
    else:
        escalado = math.ldexp(base, intento)

    return escalado * fraccion
