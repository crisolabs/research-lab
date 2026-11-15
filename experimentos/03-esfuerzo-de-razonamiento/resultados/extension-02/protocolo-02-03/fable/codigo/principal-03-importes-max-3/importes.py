import re

# Espacios exteriores opcionales, signo opcional, uno o más dígitos y,
# opcionalmente, coma con uno o dos decimales. Las clases se escriben a mano
# porque las abreviaturas de `re` también aceptan dígitos y espacios no ASCII.
_ESPACIOS = r"[ \t\n\r\f\v]*"
_FORMATO = re.compile(
    _ESPACIOS + r"([+-]?)([0-9]+)(?:,([0-9]{1,2}))?" + _ESPACIOS
)

# int() nunca aplica su tope de dígitos a textos de hasta 640 dígitos.
_DIGITOS_POR_TRAMO = 512


def _a_entero(digitos):
    # Convierte por mitades: así la cantidad de dígitos aceptada no depende
    # del tope configurable de int().
    if len(digitos) <= _DIGITOS_POR_TRAMO:
        return int(digitos)
    medio = len(digitos) // 2
    alta, baja = digitos[:medio], digitos[medio:]
    return _a_entero(alta) * 10 ** len(baja) + _a_entero(baja)


def centavos(texto):
    # type() y no isinstance(): un objeto que sólo simula `__class__`
    # (mock, proxy) no es un string.
    if not issubclass(type(texto), str):
        raise ValueError(f"se esperaba un string, no {type(texto).__name__}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, decimales = coincidencia.groups(default="")
    valor = _a_entero(entero + decimales.ljust(2, "0"))
    return -valor if signo == "-" else valor
