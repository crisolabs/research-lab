import re

# Espacios exteriores opcionales, signo opcional, uno o más dígitos ASCII y,
# opcionalmente, coma seguida de uno o dos dígitos. [0-9] se usa en lugar de \d
# para no aceptar dígitos Unicode.
_FORMATO = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    """Convierte un importe en texto (p. ej. "-12,3") a un entero de centavos."""
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    m = _FORMATO.fullmatch(texto.strip(" "))
    if m is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")

    signo, entero, decimales = m.groups()
    # "3" -> 30 centavos, "01" -> 1 centavo, ausente -> 0.
    cent = int((decimales or "").ljust(2, "0"))
    total = int(entero) * 100 + cent
    return -total if signo == "-" else total
