import math


def _numero_finito(nombre, valor):
    """Valida un int/float (no bool) representable como float finito.

    Devuelve el valor como ``int`` o ``float`` puro, conservando si era entero
    para no perder precisión en las comparaciones y en el cálculo.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser int o float, no {type(valor).__name__}")
    valor = int(valor) if isinstance(valor, int) else float(valor)
    try:
        finito = math.isfinite(valor)
    except OverflowError:  # entero demasiado grande para convertirse a float
        finito = False
    if not finito:
        raise ValueError(f"{nombre} debe ser un número finito representable como float")
    return valor


def _exponente(x):
    """Devuelve el entero e tal que 2^(e-1) <= x < 2^e, para x > 0."""
    if isinstance(x, int):
        return x.bit_length()
    return math.frexp(x)[1]


def espera(intento, base, tope, fraccion):
    """Devuelve min(tope, base * 2^intento) * fraccion.

    No genera azar: el jitter lo aporta quien llama mediante ``fraccion``.
    Lanza ``ValueError`` si algún parámetro es inválido.
    """
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError(f"intento debe ser int, no {type(intento).__name__}")
    intento = int(intento)
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    base = _numero_finito("base", base)
    tope = _numero_finito("tope", tope)
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    fraccion = _numero_finito("fraccion", fraccion)
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    # base * 2^intento >= 2^(eb - 1 + intento). Si eso ya alcanza 2^et > tope,
    # el resultado está saturado en el tope y no hace falta calcular la
    # potencia (que para intentos enormes sería un entero gigante o desbordaría).
    holgura = _exponente(tope) - _exponente(base)
    if intento > holgura:
        return tope * fraccion

    # Acá base * 2^intento < 2^et <= 2^1024: el cálculo es exacto y acotado.
    if isinstance(base, int):
        crecida = base << intento
    else:
        crecida = math.ldexp(base, intento)
    return min(tope, crecida) * fraccion
