from itertools import islice


def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")
    it = iter(elementos)
    resultado = []
    while True:
        lote = list(islice(it, tamano))
        if not lote:
            return resultado
        resultado.append(lote)
