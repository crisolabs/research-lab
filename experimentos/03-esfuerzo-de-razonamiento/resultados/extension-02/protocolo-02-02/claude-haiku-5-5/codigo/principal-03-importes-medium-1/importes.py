import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")
    m = _PATRON.fullmatch(texto.strip(" "))
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    valor = int(enteros) * 100 + int((decimales or "").ljust(2, "0") or "0")
    return -valor if signo == "-" else valor
