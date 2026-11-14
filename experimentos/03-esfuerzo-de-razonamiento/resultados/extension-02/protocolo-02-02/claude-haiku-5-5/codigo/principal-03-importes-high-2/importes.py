import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un str")
    coincidencia = _PATRON.fullmatch(texto.strip(" "))
    if coincidencia is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, entero, decimales = coincidencia.groups()
    total = int(entero) * 100 + int((decimales or "").ljust(2, "0"))
    return -total if signo == "-" else total
