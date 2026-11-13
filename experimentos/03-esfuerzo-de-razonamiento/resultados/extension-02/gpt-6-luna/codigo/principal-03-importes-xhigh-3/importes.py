import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un texto")

    coincidencia = re.fullmatch(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip())
    if coincidencia is None:
        raise ValueError("formato de importe inválido")

    signo, unidades, fraccion = coincidencia.groups()
    centimos = int(unidades) * 100
    if fraccion is not None:
        centimos += int(fraccion.ljust(2, "0"))

    return -centimos if signo == "-" else centimos
