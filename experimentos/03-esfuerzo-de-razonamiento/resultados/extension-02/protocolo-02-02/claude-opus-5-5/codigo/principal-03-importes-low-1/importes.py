import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", re.ASCII)


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un string")
    m = _PATRON.fullmatch(texto.strip(" \t\n\r\f\v"))
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, decimales = m.groups()
    valor = int(entero) * 100 + int((decimales or "").ljust(2, "0"))
    return -valor if signo == "-" else valor
