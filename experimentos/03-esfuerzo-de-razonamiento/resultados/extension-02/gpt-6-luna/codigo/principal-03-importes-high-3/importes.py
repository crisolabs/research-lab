import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    texto = texto.strip()
    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto)
    if coincidencia is None:
        raise ValueError("formato de importe inválido")

    signo, enteros, fraccion = coincidencia.groups()
    importe_entero = 0
    for digito in enteros:
        importe_entero = importe_entero * 10 + (ord(digito) - ord("0"))

    centavos = importe_entero * 100
    if fraccion is not None:
        centavos += int(fraccion.ljust(2, "0"))

    if signo == "-":
        centavos = -centavos
    return centavos
