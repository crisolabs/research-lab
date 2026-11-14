import re

_PATRON = re.compile(r"[+-]?[0-9]+(?:,[0-9]{1,2})?")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")
    limpio = texto.strip(" ")
    if not _PATRON.fullmatch(limpio):
        raise ValueError(f"formato de importe inválido: {texto!r}")

    signo = -1 if limpio.startswith("-") else 1
    if limpio[0] in "+-":
        limpio = limpio[1:]

    parte_entera, _, parte_decimal = limpio.partition(",")
    decimal = int(parte_decimal.ljust(2, "0"))
    return signo * (int(parte_entera) * 100 + decimal)
