import re


_IMPORTE = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?\Z")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    coincidencia = _IMPORTE.fullmatch(texto.strip())
    if coincidencia is None:
        raise ValueError("formato de importe inválido")

    signo, unidades, fraccion = coincidencia.groups()
    centavos = int(unidades) * 100
    if fraccion is not None:
        centavos += int(fraccion.ljust(2, "0"))

    return -centavos if signo == "-" else centavos
