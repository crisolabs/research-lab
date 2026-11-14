import re
import string

# Signo opcional, uno o más dígitos y, opcionalmente, coma seguida de uno o
# dos dígitos. Se usa [0-9] y no \d porque \d también acepta dígitos no ASCII.
_IMPORTE = re.compile(r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?")


def centavos(texto):
    """Convierte un importe como "12,3", "-0,01" o "  +7  " a centavos (int).

    Los espacios exteriores admitidos son los espacios en blanco ASCII. Todo
    otro tipo o formato lanza ValueError. Sólo se usa aritmética entera.
    """
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    coincidencia = _IMPORTE.fullmatch(texto.strip(string.whitespace))
    if coincidencia is None:
        raise ValueError(f"importe con formato inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    # Los decimales se completan a dos dígitos: "12,3" -> "1230".
    magnitud = _a_entero(enteros + (decimales or "").ljust(2, "0"))
    return -magnitud if signo == "-" else magnitud


def _a_entero(digitos):
    """Convierte una cadena de dígitos ASCII a int, sin importar su largo."""
    try:
        return int(digitos)
    except ValueError:
        # Supera sys.get_int_max_str_digits(): se convierte por mitades.
        mitad = len(digitos) // 2
        bajos = digitos[mitad:]
        return _a_entero(digitos[:mitad]) * 10 ** len(bajos) + _a_entero(bajos)
