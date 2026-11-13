import re

_FORMATO = re.compile(r"[+-]?[0-9]+(?:,[0-9]{1,2})?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    valor = texto.strip()
    if _FORMATO.fullmatch(valor) is None:
        raise ValueError("formato de importe inválido")

    signo = 1
    if valor[0] in "+-":
        if valor[0] == "-":
            signo = -1
        valor = valor[1:]

    enteros, coma, fraccion = valor.partition(",")
    resultado = int(enteros) * 100
    if coma:
        resultado += int(fraccion.ljust(2, "0"))

    return signo * resultado
