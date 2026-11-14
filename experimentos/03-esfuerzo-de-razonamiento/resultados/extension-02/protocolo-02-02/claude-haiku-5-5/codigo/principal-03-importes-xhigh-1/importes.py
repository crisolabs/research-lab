import re
from decimal import Decimal

_IMPORTE = re.compile(r"[ ]*([+-]?)([0-9]+)(?:,([0-9]{1,2}))?[ ]*")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"el importe debe ser str, no {type(texto).__name__}")
    m = _IMPORTE.fullmatch(texto)
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    pesos = int(Decimal(enteros))
    fraccion = int(decimales.ljust(2, "0")) if decimales else 0
    total = pesos * 100 + fraccion
    return -total if signo == "-" else total
