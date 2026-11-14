import sys
from itertools import islice


def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo (los bool no se admiten)")

    # islice no admite límites mayores que sys.maxsize; ninguna lista puede
    # llegar a ese largo, así que acotar no cambia el resultado.
    limite = min(tamano, sys.maxsize)
    iterador = iter(elementos)
    resultado = []
    while lote := list(islice(iterador, limite)):
        resultado.append(lote)
        if len(lote) < limite:  # lote incompleto: el iterable ya se agotó
            break
    return resultado
