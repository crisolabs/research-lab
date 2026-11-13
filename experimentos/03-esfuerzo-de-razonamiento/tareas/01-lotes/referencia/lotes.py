from itertools import islice


def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamaño inválido")
    it = iter(elementos)
    salida = []
    while bloque := list(islice(it, tamano)):
        salida.append(bloque)
    return salida
