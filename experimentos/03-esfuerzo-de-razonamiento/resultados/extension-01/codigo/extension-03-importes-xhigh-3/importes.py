import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("Importe inválido")

    coincidencia = re.fullmatch(
        r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?", texto.strip()
    )
    if coincidencia is None:
        raise ValueError("Importe inválido")

    signo, parte_entera, parte_decimal = coincidencia.groups()
    importe = 0
    for digito in parte_entera:
        importe = importe * 10 + ord(digito) - ord("0")

    importe = importe * 100 + int((parte_decimal or "").ljust(2, "0"))
    return -importe if signo == "-" else importe
