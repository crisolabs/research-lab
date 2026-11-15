import re

_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# Con tramos de este largo, int() nunca aplica el límite de dígitos del intérprete.
_TRAMO = 500


def _entero(digitos):
    """Convierte dígitos ASCII a int, sin tope de longitud."""
    if len(digitos) <= _TRAMO:
        return int(digitos)
    corte = len(digitos) // 2
    return _entero(digitos[:-corte]) * 10**corte + _entero(digitos[-corte:])


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    total = _entero(enteros) * 100 + int((decimales or "").ljust(2, "0"))
    return -total if signo == "-" else total
