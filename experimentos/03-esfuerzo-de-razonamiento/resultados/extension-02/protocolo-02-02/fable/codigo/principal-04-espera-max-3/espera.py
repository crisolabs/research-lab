"""Espera exponencial con jitter."""

import math


def _es_numero_finito(valor):
    """Indica si `valor` es int/float (no bool) representable como float finito."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(float(valor))
    except OverflowError:
        # Entero demasiado grande para convertirse a float.
        return False


def _exponente(valor):
    """Devuelve el entero `e` tal que `2**(e - 1) <= valor < 2**e` (valor > 0)."""
    if isinstance(valor, int):
        return valor.bit_length()
    return math.frexp(valor)[1]


def espera(intento, base, tope, fraccion):
    """Devuelve `min(tope, base * 2**intento) * fraccion`.

    `fraccion` es el jitter y lo aporta quien llama: acá no se genera azar.
    Lanza `ValueError` si algún parámetro es inválido.
    """
    if isinstance(intento, bool) or not isinstance(intento, int) or intento < 0:
        raise ValueError("intento debe ser un entero no negativo")
    if not _es_numero_finito(base) or not _es_numero_finito(tope):
        raise ValueError(
            "base y tope deben ser números finitos representables como float"
        )
    if not 0 < base <= tope:
        raise ValueError("base y tope deben cumplir 0 < base <= tope")
    if not _es_numero_finito(fraccion) or not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe ser un número entre 0 y 1")

    # Si `intento` supera la diferencia de exponentes binarios, entonces
    # `base * 2**intento >= 2**_exponente(tope) > tope` y se devuelve el tope sin
    # construir la potencia. En caso contrario el producto es menor que
    # `2**_exponente(tope)`: es chico y se calcula de forma exacta, sin desbordar.
    if intento > _exponente(tope) - _exponente(base):
        return tope * fraccion
    if isinstance(base, int):
        sin_tope = base << intento
    else:
        sin_tope = math.ldexp(base, intento)
    return min(tope, sin_tope) * fraccion
