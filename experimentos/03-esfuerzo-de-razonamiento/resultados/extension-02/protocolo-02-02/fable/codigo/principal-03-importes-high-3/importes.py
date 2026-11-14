import re

_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# int() rechaza por defecto literales de más de 4300 dígitos; convertimos por
# tramos para que la cantidad de dígitos de la parte entera no tenga tope.
_TRAMO = 4000


def _entero(digitos):
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
    total = _entero(enteros) * 100
    if decimales:
        total += int(decimales.ljust(2, "0"))
    return -total if signo == "-" else total
