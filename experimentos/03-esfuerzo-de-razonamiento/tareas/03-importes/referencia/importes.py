import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("importe inválido")
    m = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if m is None:
        raise ValueError("importe inválido")
    signo, entero, fraccion = m.groups()
    valor = int(entero) * 100 + int((fraccion or "").ljust(2, "0"))
    return -valor if signo == "-" else valor
