"""Espera exponencial con jitter."""

import math


def _entero_no_negativo(nombre, valor):
    """Valida un entero >= 0 (no booleano) y lo devuelve como int nativo."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{nombre} debe ser un entero (no booleano)")
    if valor < 0:
        raise ValueError(f"{nombre} no puede ser negativo")
    return int(valor)


def _real_finito(nombre, valor):
    """Valida un int/float finito (no booleano) y lo devuelve como tipo nativo.

    Un entero sólo es válido si puede convertirse a un float finito.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser un número int o float (no booleano)")
    if isinstance(valor, float):
        valor = float(valor)
        if not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito")
        return valor
    valor = int(valor)
    try:
        float(valor)
    except OverflowError:
        raise ValueError(
            f"{nombre} es demasiado grande para representarse como float"
        ) from None
    return valor


def _exponente_binario(valor):
    """Devuelve e tal que 2**(e - 1) <= valor < 2**e, para valor > 0."""
    if isinstance(valor, int):
        return valor.bit_length()
    return math.frexp(valor)[1]


def _crecimiento_acotado(intento, base, tope):
    """Calcula min(tope, base * 2**intento) sin construir 2**intento."""
    # base * 2**intento >= 2**(e_base - 1 + intento) y tope < 2**e_tope: si el
    # intento alcanza e_tope - e_base + 1, el crecimiento ya superó al tope.
    if intento >= _exponente_binario(tope) - _exponente_binario(base) + 1:
        return tope
    # Acá base * 2**intento < 2**e_tope: el cálculo exacto es chico y no desborda.
    if isinstance(base, int):
        crecido = base << intento
    else:
        crecido = math.ldexp(base, intento)
    return crecido if crecido < tope else tope


def espera(intento, base, tope, fraccion):
    """Devuelve min(tope, base * 2**intento) * fraccion.

    intento: entero no negativo (no booleano).
    base, tope: int/float finitos (no booleanos), representables como float
        finito, con 0 < base <= tope.
    fraccion: int/float finito (no booleano) entre 0 y 1 inclusive; es el
        jitter, que debe proveer quien llama.

    Lanza ValueError si algún parámetro es inválido.
    """
    intento = _entero_no_negativo("intento", intento)
    base = _real_finito("base", base)
    tope = _real_finito("tope", tope)
    fraccion = _real_finito("fraccion", fraccion)
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")
    return _crecimiento_acotado(intento, base, tope) * fraccion
