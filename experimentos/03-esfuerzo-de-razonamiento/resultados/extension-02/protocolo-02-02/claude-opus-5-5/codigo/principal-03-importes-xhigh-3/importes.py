import re

_PATRON = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un string")
    coincidencia = _PATRON.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    decimales = (decimales or "").ljust(2, "0")
    valor = int(enteros) * 100 + int(decimales)
    return -valor if signo == "-" else valor
