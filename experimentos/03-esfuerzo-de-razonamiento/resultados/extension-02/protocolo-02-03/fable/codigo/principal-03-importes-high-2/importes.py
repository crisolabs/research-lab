import re

_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# int() rechaza cadenas decimales muy largas (límite configurable, mínimo 640
# dígitos), así que los importes enormes se convierten por tramos.
_TRAMO = 600


def _a_entero(digitos):
    valor = 0
    for i in range(0, len(digitos), _TRAMO):
        tramo = digitos[i:i + _TRAMO]
        valor = valor * 10 ** len(tramo) + int(tramo)
    return valor


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"importe inválido: {texto!r}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    total = _a_entero(enteros) * 100 + int((decimales or "").ljust(2, "0"))
    return -total if signo == "-" else total
