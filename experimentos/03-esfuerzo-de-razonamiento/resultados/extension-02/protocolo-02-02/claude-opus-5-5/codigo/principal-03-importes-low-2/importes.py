import re

_PATRON = re.compile(r"[ \t\n\r\f\v]*([+-]?)([0-9]+)(?:,([0-9]{1,2}))?[ \t\n\r\f\v]*\Z")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un string")
    m = _PATRON.match(texto)
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    valor = int(enteros) * 100 + int((decimales or "").ljust(2, "0"))
    return -valor if signo == "-" else valor
