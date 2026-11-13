def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un entero positivo")

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
            return resultado

        resultado.append(lote)
