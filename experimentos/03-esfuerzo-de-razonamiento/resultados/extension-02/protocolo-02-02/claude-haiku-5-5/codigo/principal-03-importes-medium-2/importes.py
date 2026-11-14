import re

_PATRON = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    """Convierte un importe en texto (p. ej. "-0,01") a un entero de centavos.

    Acepta sólo: espacios exteriores opcionales, signo "+" o "-" opcional,
    uno o más dígitos ASCII y, opcionalmente, coma seguida de uno o dos dígitos.
    Cualquier otro formato o tipo genera ValueError.
    """
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un str")

    coincidencia = _PATRON.fullmatch(texto.strip(" "))
    if coincidencia is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")

    signo, enteros, decimales = coincidencia.groups()
    if decimales is None:
        decimales = ""
    # Una sola cifra decimal equivale a décimas: "12,3" -> 30 centavos.
    decimales = decimales.ljust(2, "0")

    total = int(enteros) * 100 + int(decimales)
    return -total if signo == "-" else total
