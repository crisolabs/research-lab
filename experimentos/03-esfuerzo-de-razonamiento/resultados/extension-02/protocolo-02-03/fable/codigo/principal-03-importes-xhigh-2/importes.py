import re

_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# CPython limita la longitud de las cadenas decimales que convierte int()
# (configurable, pero nunca por debajo de 640 dígitos).
_MAX_DIGITOS_INT = 600


def _entero(digitos):
    if len(digitos) <= _MAX_DIGITOS_INT:
        return int(digitos)
    bajos = len(digitos) // 2
    return _entero(digitos[:-bajos]) * 10**bajos + _entero(digitos[-bajos:])


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    total = _entero(enteros) * 100
    if decimales:
        total += int(decimales.ljust(2, "0"))
    return -total if signo == "-" else total
