import re

_IMPORTE = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def _entero(digitos):
    # int() de strings muy largos supera el límite de dígitos de Python;
    # se convierte por trozos para no rechazar importes válidos.
    total = 0
    for i in range(0, len(digitos), 1000):
        trozo = digitos[i:i + 1000]
        total = total * 10 ** len(trozo) + int(trozo)
    return total


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un str")
    coincidencia = _IMPORTE.fullmatch(texto.strip(" "))
    if coincidencia is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    decimales = (decimales or "").ljust(2, "0")
    valor = _entero(enteros) * 100 + int(decimales)
    return -valor if signo == "-" else valor
