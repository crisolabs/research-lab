import re

_FORMATO = re.compile(r" *([+-]?)([0-9]+)(?:,([0-9]{1,2}))? *")


def _a_entero(digitos):
    # int() de str tiene un límite de dígitos (4300 por defecto); se convierte por bloques.
    valor = 0
    for i in range(0, len(digitos), 500):
        bloque = digitos[i:i + 500]
        valor = valor * 10 ** len(bloque) + int(bloque)
    return valor


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError(f"se esperaba str, no {type(texto).__name__}")
    coincidencia = _FORMATO.fullmatch(texto)
    if coincidencia is None:
        raise ValueError(f"importe inválido: {texto!r}")
    signo, enteros, decimales = coincidencia.groups()
    cent = _a_entero(enteros + (decimales or "").ljust(2, "0"))
    return -cent if signo == "-" else cent
