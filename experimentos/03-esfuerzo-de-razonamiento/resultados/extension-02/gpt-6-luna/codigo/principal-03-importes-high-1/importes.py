import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    importe = texto.strip()
    if re.fullmatch(r"[+-]?[0-9]+(?:,[0-9]{1,2})?", importe) is None:
        raise ValueError("formato de importe inválido")

    negativo = importe.startswith("-")
    sin_signo = importe[1:] if importe[:1] in "+-" else importe
    entero, separador, fraccion = sin_signo.partition(",")
    total = int(entero) * 100
    if separador:
        total += int(fraccion.ljust(2, "0"))

    return -total if negativo else total
