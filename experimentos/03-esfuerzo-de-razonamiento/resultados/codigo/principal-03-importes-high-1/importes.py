import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    partes = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if partes is None:
        raise ValueError("Formato de importe inválido")

    entero = 0
    for digito in partes[2]:
        entero = entero * 10 + ord(digito) - ord("0")
    fraccion = (partes[3] or "").ljust(2, "0")
    importe = entero * 100 + int(fraccion)
    return -importe if partes[1] == "-" else importe
