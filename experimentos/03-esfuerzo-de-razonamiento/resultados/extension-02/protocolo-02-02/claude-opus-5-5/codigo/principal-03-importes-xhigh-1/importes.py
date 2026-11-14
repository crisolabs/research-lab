import re

_PATRON = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")
_BLOQUE = 1000


def _digitos_a_entero(digitos):
    # Conversión por bloques para no depender del límite de int() con
    # cadenas decimales muy largas (sys.int_max_str_digits).
    valor = 0
    for inicio in range(0, len(digitos), _BLOQUE):
        bloque = digitos[inicio:inicio + _BLOQUE]
        valor = valor * 10 ** len(bloque) + int(bloque)
    return valor


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("se esperaba un str")
    coincidencia = _PATRON.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, entero, fraccion = coincidencia.groups()
    fraccion = (fraccion or "").ljust(2, "0")
    resultado = _digitos_a_entero(entero) * 100 + int(fraccion)
    return -resultado if signo == "-" else resultado
