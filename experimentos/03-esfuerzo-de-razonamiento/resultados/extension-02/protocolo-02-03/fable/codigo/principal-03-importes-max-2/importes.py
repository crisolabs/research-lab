import re

# Formato exacto: espacios exteriores, signo opcional, dígitos ASCII y,
# opcionalmente, coma seguida de uno o dos dígitos. Se usan "[ ]" y "[0-9]" en
# lugar de "\s" y "\d", que además aceptan tabulaciones, saltos de línea y
# espacios y dígitos no ASCII.
_FORMATO = re.compile(r"[ ]*([+-]?)([0-9]+)(?:,([0-9]{1,2}))?[ ]*")


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba un str, no {type(texto).__name__}")
    # fullmatch y no "$": este último toleraría un salto de línea final.
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, fraccion = coincidencia.groups(default="")
    # Sólo aritmética entera: la fracción se completa a dos dígitos ("3" -> "30").
    valor = int(entero + fraccion.ljust(2, "0"))
    return -valor if signo == "-" else valor
