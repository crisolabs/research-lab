import math
import sys

# Todo float finito (y todo int convertible a float) es menor que 2**_EXP_MAX.
_EXP_MAX = sys.float_info.max_exp


def _numero(nombre, valor):
    """Valida un int/float no booleano representable como float finito.

    Devuelve el valor normalizado a int o float exactos (sin subclases).
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser un int o float, no booleano")
    if isinstance(valor, int):
        valor = int.__index__(valor)
        try:
            float(valor)
        except OverflowError:
            raise ValueError(
                f"{nombre} es demasiado grande para representarse como float"
            ) from None
    else:
        valor = float.__float__(valor)
        if not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito")
    return valor


def espera(intento, base, tope, fraccion):
    """Devuelve min(tope, base·2^intento) · fraccion.

    `fraccion` es el factor de jitter que provee quien llama. Funciona con
    intentos enormes sin desbordar ni construir enteros exponenciales.
    """
    if isinstance(intento, bool) or not isinstance(intento, int):
        raise ValueError("intento debe ser un entero, no booleano")
    intento = int.__index__(intento)
    if intento < 0:
        raise ValueError("intento no puede ser negativo")
    base = _numero("base", base)
    tope = _numero("tope", tope)
    fraccion = _numero("fraccion", fraccion)
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    # Exponente exacto tal que 2^(exp_base - 1) <= base < 2^exp_base.
    if isinstance(base, int):
        exp_base = base.bit_length()
    else:
        exp_base = math.frexp(base)[1]
    # base·2^intento >= 2^(exp_base - 1 + intento) >= 2^_EXP_MAX > tope.
    if exp_base - 1 + intento >= _EXP_MAX:
        return tope * fraccion
    # Aquí base·2^intento < 2^_EXP_MAX: el producto es exacto y acotado.
    if isinstance(base, int):
        crecido = base << intento
    else:
        crecido = math.ldexp(base, intento)
    return min(tope, crecido) * fraccion
