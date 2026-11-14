"""Conversión de importes escritos con coma decimal a centavos enteros."""

import re

# Formato completo admitido: espacios exteriores opcionales (sólo U+0020), signo
# opcional, uno o más dígitos ASCII y, opcionalmente, coma con uno o dos dígitos.
# Se usa [0-9] y no \d (que acepta dígitos Unicode), y fullmatch() y no $ (que
# admite un salto de línea final).
_IMPORTE = re.compile(
    r"""
    [ ]*
    (?P<signo>[+-]?)
    (?P<unidades>[0-9]+)
    (?:,(?P<decimales>[0-9]{1,2}))?
    [ ]*
    """,
    re.VERBOSE,
)

# Mínimo valor admitido por sys.set_int_max_str_digits(): int() siempre puede
# convertir cadenas de esta longitud; las más largas se convierten por tramos.
_MAX_DIGITOS_INT = 640


def _entero(digitos):
    """Convierte una cadena de dígitos ASCII ya validada en int, de cualquier longitud."""
    if len(digitos) <= _MAX_DIGITOS_INT:
        return int(digitos)
    mitad = len(digitos) // 2
    return _entero(digitos[:-mitad]) * 10**mitad + _entero(digitos[-mitad:])


def centavos(texto):
    """Convierte un importe como ``"-12,3"`` en un entero de centavos (``-1230``).

    Lanza ValueError si ``texto`` no es un str o no respeta el formato admitido.
    """
    # type() y no isinstance(), que se deja engañar por __class__ (p. ej. Mock(spec=str)).
    if not issubclass(type(texto), str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    texto = str.__str__(texto)  # copia como str exacto si llega una subclase
    partes = _IMPORTE.fullmatch(texto)
    if partes is None:
        raise ValueError(f"formato de importe inválido: {texto!r}")
    resultado = _entero(partes["unidades"]) * 100
    if partes["decimales"] is not None:
        resultado += int(partes["decimales"].ljust(2, "0"))
    return -resultado if partes["signo"] == "-" else resultado
