import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un string")
    m = _PATRON.fullmatch(texto.strip(" \t\n\r\f\v"))
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    decimales = (decimales or "").ljust(2, "0")
    valor = int(enteros) * 100 + int(decimales)
    return -valor if signo == "-" else valor
