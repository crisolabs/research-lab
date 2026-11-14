from itertools import islice


def lotes(elementos, tamano):
    """Devuelve una lista de listas con hasta `tamano` elementos cada una."""
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")
    iterador = iter(elementos)
    resultado = []
    while True:
        lote = list(islice(iterador, tamano))
        if not lote:
            return resultado
        resultado.append(lote)
