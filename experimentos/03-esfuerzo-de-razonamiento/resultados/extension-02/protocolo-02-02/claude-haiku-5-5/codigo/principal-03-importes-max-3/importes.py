import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def _entero(digitos):
    # int() de Python rechaza strings de más de 4300 dígitos, así que se
    # convierte por bloques para aceptar cualquier cantidad de dígitos.
    valor = 0
    for i in range(0, len(digitos), 1000):
        bloque = digitos[i:i + 1000]
        valor = valor * 10 ** len(bloque) + int(bloque)
    return valor


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba str, no {type(texto).__name__}")
    m = _PATRON.fullmatch(texto.strip(" "))
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, decimales = m.groups()
    valor = _entero(entero + (decimales or "").ljust(2, "0"))
    return -valor if signo == "-" else valor
