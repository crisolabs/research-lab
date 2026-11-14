import re

_PATRON = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un str")
    m = _PATRON.fullmatch(texto)
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, entero, decimales = m.groups()
    total = int(entero) * 100 + int((decimales or "").ljust(2, "0"))
    return -total if signo == "-" else total
