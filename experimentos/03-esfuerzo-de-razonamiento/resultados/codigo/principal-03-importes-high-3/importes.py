import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if coincidencia is None:
        raise ValueError("Formato de importe inválido")

    signo, parte_entera, parte_decimal = coincidencia.groups()
    entero = 0
    for digito in parte_entera:
        entero = entero * 10 + ord(digito) - ord("0")

    decimal = int((parte_decimal or "").ljust(2, "0"))
    resultado = entero * 100 + decimal
    return -resultado if signo == "-" else resultado
