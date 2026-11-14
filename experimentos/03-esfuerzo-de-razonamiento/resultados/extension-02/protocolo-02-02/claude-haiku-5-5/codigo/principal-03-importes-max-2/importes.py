import re

_IMPORTE = re.compile(r"[ ]*([+-]?)([0-9]+)(?:,([0-9]{1,2}))?[ ]*")
# int(str) rechaza strings de más de 4300 dígitos desde Python 3.11; se convierte por bloques.
_BLOQUE = 1000


def _a_entero(digitos):
    valor = 0
    for i in range(0, len(digitos), _BLOQUE):
        bloque = digitos[i:i + _BLOQUE]
        valor = valor * 10 ** len(bloque) + int(bloque)
    return valor


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"importe no es texto: {type(texto).__name__}")
    m = _IMPORTE.fullmatch(texto)
    if m is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = m.groups()
    total = _a_entero(enteros) * 100 + int((decimales or "").ljust(2, "0"))
    return -total if signo == "-" else total
