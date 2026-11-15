import re

# Espacios exteriores, signo opcional, dígitos ASCII y, opcionalmente, coma
# con uno o dos decimales. Se usa [0-9] y no \d porque \d acepta dígitos no
# ASCII, y fullmatch y no "$" porque "$" tolera un salto de línea final.
_IMPORTE = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# int() rechaza cadenas más largas que sys.get_int_max_str_digits(), límite
# que nunca puede configurarse por debajo de 640 dígitos.
_TRAMO = 512


def _entero(digitos):
    """Convierte dígitos ASCII a int sin depender del límite de int()."""
    if len(digitos) <= _TRAMO:
        return int(digitos)
    corte = len(digitos) // 2
    alto, bajo = digitos[:corte], digitos[corte:]
    return _entero(alto) * 10 ** len(bajo) + _entero(bajo)


def centavos(texto):
    """Convierte un importe como "12,3" o "-0,01" a un entero de centavos.

    Lanza ValueError si `texto` no es un str con el formato esperado.
    """
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    coincidencia = _IMPORTE.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    total = _entero(enteros) * 100
    if decimales:
        total += int(decimales.ljust(2, "0"))
    return -total if signo == "-" else total
