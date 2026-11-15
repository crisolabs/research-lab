import re

_ESPACIOS = " \t\n\r\f\v"
_FORMATO = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"importe inválido: {texto!r}")
    m = _FORMATO.fullmatch(texto.strip(_ESPACIOS))
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, decimales = m.groups()
    valor = int(entero) * 100 + int((decimales or "").ljust(2, "0") or "0")
    return -valor if signo == "-" else valor
