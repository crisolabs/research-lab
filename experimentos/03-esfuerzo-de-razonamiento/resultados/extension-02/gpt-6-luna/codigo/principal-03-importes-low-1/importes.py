import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    texto = texto.strip()
    if re.fullmatch(r"[+-]?[0-9]+(?:,[0-9]{1,2})?", texto) is None:
        raise ValueError("formato de importe inválido")

    negativo = texto.startswith("-")
    if texto[:1] in ("+", "-"):
        texto = texto[1:]

    partes = texto.split(",", 1)
    unidades = int(partes[0])
    fraccion = (partes[1] if len(partes) == 2 else "").ljust(2, "0")
    resultado = unidades * 100 + int(fraccion or "0")
    return -resultado if negativo else resultado
