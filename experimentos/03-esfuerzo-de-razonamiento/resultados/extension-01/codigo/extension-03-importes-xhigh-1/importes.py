import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    coincidencia = re.fullmatch(
        r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip()
    )
    if coincidencia is None:
        raise ValueError("Formato de importe inválido")

    signo, entero, fraccion = coincidencia.groups()
    digitos = entero + (fraccion or "").ljust(2, "0")
    resultado = 0
    for digito in digitos:
        resultado = resultado * 10 + ord(digito) - ord("0")

    return -resultado if signo == "-" else resultado
