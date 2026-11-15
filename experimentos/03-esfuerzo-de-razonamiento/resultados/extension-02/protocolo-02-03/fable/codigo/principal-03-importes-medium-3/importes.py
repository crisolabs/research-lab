import re

_PATRON = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"importe inválido: {texto!r}")
    m = _PATRON.fullmatch(texto)
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    total = int(enteros) * 100
    if decimales:
        total += int(decimales.ljust(2, "0"))
    return -total if signo == "-" else total
