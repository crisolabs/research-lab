import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    partes = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if partes is None:
        raise ValueError("Formato de importe inválido")

    enteros = 0
    for digito in partes.group(2):
        enteros = enteros * 10 + ord(digito) - ord("0")

    decimales = (partes.group(3) or "").ljust(2, "0")
    importe = enteros * 100 + int(decimales)
    return -importe if partes.group(1) == "-" else importe
