import re

# Espacios exteriores opcionales, signo opcional, uno o más dígitos ASCII y,
# opcionalmente, coma seguida de uno o dos dígitos ASCII. Se usa [0-9] y no \d
# (que en str acepta dígitos Unicode), y fullmatch en vez de "$" (que admite un
# salto de línea final).
_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")

# int(str) rechaza cadenas de más de sys.get_int_max_str_digits() dígitos
# (4300 por defecto), pero nunca aplica ese límite hasta los 640 dígitos.
_MAX_DIGITOS_INT = 640


def _a_entero(digitos):
    """Convierte una cadena de dígitos ASCII en int, sin límite de longitud."""
    if len(digitos) <= _MAX_DIGITOS_INT:
        return int(digitos)
    mitad = len(digitos) // 2
    altos, bajos = digitos[:mitad], digitos[mitad:]
    return _a_entero(altos) * 10 ** len(bajos) + _a_entero(bajos)


def centavos(texto):
    """Convierte un importe como "12,3", "-0,01" o "  +7  " en centavos (int).

    Lanza ValueError si `texto` no es un str o no respeta exactamente el formato.
    """
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    # La parte entera seguida de los decimales completados a dos dígitos son
    # exactamente los centavos: no hace falta aritmética de punto flotante.
    valor = _a_entero(enteros + (decimales or "").ljust(2, "0"))
    return -valor if signo == "-" else valor
