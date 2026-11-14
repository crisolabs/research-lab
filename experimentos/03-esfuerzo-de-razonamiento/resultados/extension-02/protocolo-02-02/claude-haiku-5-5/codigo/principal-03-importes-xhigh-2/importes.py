import re

_FORMATO = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"el importe debe ser str, no {type(texto).__name__}")
    m = _FORMATO.fullmatch(texto.strip(" "))
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, entero, decimal = m.groups()
    total = int(entero) * 100 + int((decimal or "").ljust(2, "0"))
    return -total if signo == "-" else total
