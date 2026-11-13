import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if coincidencia is None:
        raise ValueError("Formato de importe inválido")

    signo, enteros, decimales = coincidencia.groups()
    resultado = 0
    for digito in enteros:
        resultado = resultado * 10 + ord(digito) - ord("0")
    resultado *= 100
    if decimales is not None:
        resultado += (ord(decimales[0]) - ord("0")) * 10
        if len(decimales) == 2:
            resultado += ord(decimales[1]) - ord("0")

    return -resultado if signo == "-" else resultado
