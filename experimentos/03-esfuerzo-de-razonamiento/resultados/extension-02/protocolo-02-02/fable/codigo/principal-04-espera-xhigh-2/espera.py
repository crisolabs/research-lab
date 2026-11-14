import math

# Un float positivo vale como mínimo 2**-1074 y un tope representable es menor
# que 2**1024: a partir de este intento, base * 2**intento siempre alcanza el
# tope, así que no hace falta calcular la potencia.
_INTENTO_SATURADO = 1074 + 1024


def _es_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_duracion(valor, nombre):
    if not _es_numero(valor):
        raise ValueError(f"{nombre} debe ser un número int o float")
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


def espera(intento, base, tope, fraccion):
    if not isinstance(intento, int) or isinstance(intento, bool):
        raise ValueError("intento debe ser un entero")
    if intento < 0:
        raise ValueError("intento no puede ser negativo")

    _validar_duracion(base, "base")
    _validar_duracion(tope, "tope")
    if not 0 < base <= tope:
        raise ValueError("se requiere 0 < base <= tope")

    if not _es_numero(fraccion):
        raise ValueError("fraccion debe ser un número int o float")
    # La comparación también descarta NaN, infinitos y enteros gigantes.
    if not 0 <= fraccion <= 1:
        raise ValueError("fraccion debe estar entre 0 y 1 inclusive")

    if intento >= _INTENTO_SATURADO:
        return tope * fraccion

    if isinstance(base, int):
        # Acotado: base < 2**1024 e intento < _INTENTO_SATURADO.
        crecido = base << intento
    else:
        try:
            # Escalar por una potencia de dos es exacto salvo desborde.
            crecido = math.ldexp(base, intento)
        except OverflowError:
            crecido = math.inf

    return min(tope, crecido) * fraccion
