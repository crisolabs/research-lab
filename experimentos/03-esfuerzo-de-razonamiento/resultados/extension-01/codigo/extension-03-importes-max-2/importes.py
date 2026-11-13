import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    texto = texto.strip()
    if re.fullmatch(r"[+-]?[0-9]+(?:,[0-9]{1,2})?", texto) is None:
        raise ValueError("Formato de importe inválido")

    signo = -1 if texto.startswith("-") else 1
    parte_entera, _, parte_decimal = texto.lstrip("+-").partition(",")
    resultado = 0
    for digito in parte_entera + parte_decimal.ljust(2, "0"):
        resultado = resultado * 10 + ord(digito) - ord("0")
    return signo * resultado
