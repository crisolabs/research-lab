import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("formato de importe inválido")

    texto = texto.strip()
    if re.fullmatch(r"[+-]?[0-9]+(?:,[0-9]{1,2})?", texto) is None:
        raise ValueError("formato de importe inválido")

    negativo = texto.startswith("-")
    if texto[:1] in ("+", "-"):
        texto = texto[1:]
    partes = texto.split(",")
    centavos = int(partes[0]) * 100
    if len(partes) == 2:
        centavos += int(partes[1].ljust(2, "0"))
    return -centavos if negativo else centavos
