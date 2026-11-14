import sys
from itertools import islice


def lotes(elementos, tamano):
    # Se valida antes de tocar `elementos` para no consumir un iterador en vano.
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo (los booleanos no valen)")

    # islice no acepta límites mayores que sys.maxsize; ninguna lista puede
    # tener tantos elementos, así que acotarlo no cambia el resultado.
    limite = min(tamano, sys.maxsize)
    iterador = iter(elementos)
    resultado = []
    while True:
        lote = list(islice(iterador, limite))
        if lote:
            resultado.append(lote)
        if len(lote) < limite:
            # Lote incompleto o vacío: el iterador se agotó.
            return resultado
