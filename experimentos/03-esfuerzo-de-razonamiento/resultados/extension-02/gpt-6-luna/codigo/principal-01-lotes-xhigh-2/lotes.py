def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")

    iterador = iter(elementos)
    resultado = []

    while True:
        lote = []
        for _ in range(tamano):
            try:
                lote.append(next(iterador))
            except StopIteration:
                break

        if not lote:
            break

        resultado.append(lote)
        if len(lote) < tamano:
            break

    return resultado
