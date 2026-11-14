import sys
from itertools import islice


def lotes(elementos, tamano):
    # bool es subclase de int, por eso se excluye explícitamente. Se valida
    # antes de iterar para no consumir la entrada si el tamaño es inválido.
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")

    # islice no admite un límite mayor que sys.maxsize; ninguna lista puede
    # llegar a tantos elementos, así que acotarlo no cambia el resultado.
    paso = min(tamano, sys.maxsize)
    iterador = iter(elementos)

    resultado = []
    while True:
        lote = list(islice(iterador, paso))
        if lote:
            resultado.append(lote)
        if len(lote) < paso:
            # Lote incompleto o vacío: el iterador se agotó.
            return resultado
