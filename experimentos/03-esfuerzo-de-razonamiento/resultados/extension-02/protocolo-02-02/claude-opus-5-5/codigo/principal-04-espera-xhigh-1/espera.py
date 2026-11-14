import math

# Todo float finito es menor que 2**1024; un int representable como float
# finito también lo es.
_LIMITE_EXPONENTE = 1024


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_finito(nombre, valor):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser un número int o float (no booleano)")
    if isinstance(valor, float):
        if not math.isfinite(valor):
            raise ValueError(f"{nombre} debe ser finito")
    else:
        try:
            float(valor)
        except OverflowError:
            raise ValueError(
                f"{nombre} es demasiado grande para representarse como float"
            ) from None


def _escalar_con_tope(base, intento, tope):
    """Devuelve min(tope, base * 2**intento) sin construir enteros gigantes."""
    if isinstance(base, int):
        # 2**(bits-1) <= base < 2**bits
        bits = base.bit_length()
        if bits - 1 + intento >= _LIMITE_EXPONENTE:
            # base * 2**intento >= 2**1024 > tope
            return tope
        escalado = base << intento  # exacto y acotado (< 2**1025)
    else:
        # base = mantisa * 2**exponente, con 0.5 <= mantisa < 1
        _, exponente = math.frexp(base)
        if exponente - 1 + intento >= _LIMITE_EXPONENTE:
            # base * 2**intento >= 2**1024 > tope
            return tope
        try:
            escalado = math.ldexp(base, intento)  # exacto: sólo escala
        except OverflowError:
            return tope
    return tope if escalado >= tope else escalado


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero (no booleano)")
    if intento < 0:
        raise ValueError("intento debe ser no negativo")

    _validar_finito("base", base)
    _validar_finito("tope", tope)
    if not 0 < base:
        raise ValueError("base debe ser mayor que 0")
    if not base <= tope:
        raise ValueError("base debe ser menor o igual que tope")

    _validar_finito("fraccion", fraccion)
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    return _escalar_con_tope(base, intento, tope) * fraccion
