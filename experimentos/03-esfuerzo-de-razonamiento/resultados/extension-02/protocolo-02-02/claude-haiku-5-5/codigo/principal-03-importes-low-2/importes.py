import re

_PATRON = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un str")
    m = _PATRON.fullmatch(texto)
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, entero, decimales = m.groups()
    decimales = (decimales or "").ljust(2, "0")
    total = int(entero) * 100 + int(decimales)
    return -total if signo == "-" else total
