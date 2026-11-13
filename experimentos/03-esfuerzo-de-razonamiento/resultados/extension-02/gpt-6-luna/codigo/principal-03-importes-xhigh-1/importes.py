import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip(" "))
    if coincidencia is None:
        raise ValueError("formato de importe inválido")

    signo, unidades, fraccion = coincidencia.groups()
    total = int(unidades) * 100 + int((fraccion or "").ljust(2, "0") or "0")
    return -total if signo == "-" else total
