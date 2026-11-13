import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("importe inválido")

    texto = texto.strip()
    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto)
    if coincidencia is None:
        raise ValueError("importe inválido")

    signo, unidades, fraccion = coincidencia.groups()
    centavos = int(unidades) * 100 + int((fraccion or "").ljust(2, "0"))
    return -centavos if signo == "-" else centavos
