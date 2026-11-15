import math


def _es_numero_finito(valor):
    # bool es subclase de int, por eso se descarta explícitamente.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(valor)
    except OverflowError:
        # Entero demasiado grande para representarse como float.
        return False


def _exponente(valor):
    # Para valor > 0 devuelve e tal que 2**(e - 1) <= valor < 2**e.
    if isinstance(valor, int):
        return valor.bit_length()
    return math.frexp(valor)[1]


def espera(intento, base, tope, fraccion):
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not _es_numero_finito(base) or not _es_numero_finito(tope):
        raise ValueError(
            "base y tope deben ser números finitos representables como float"
        )
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not _es_numero_finito(fraccion) or not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe ser un número entre 0 y 1 inclusive")

    # base * 2**intento >= 2**(e_base - 1 + intento). Si intento supera la
    # diferencia de exponentes, ese valor ya es >= 2**e_tope > tope, así que el
    # resultado es el tope sin necesidad de calcular la potencia.
    if intento > _exponente(tope) - _exponente(base):
        return tope * fraccion

    # Acá base * 2**intento < 2**e_tope: el cálculo es exacto, acotado por la
    # magnitud de tope, y no puede desbordar.
    if isinstance(base, int):
        escalado = base << intento
    else:
        escalado = math.ldexp(base, intento)
    return min(tope, escalado) * fraccion
