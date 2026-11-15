def lotes(elementos, tamano):
    # Se valida antes de iterar para no consumir un iterable de una sola
    # pasada si el tamaño es inválido. bool es subclase de int: va aparte.
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")

    resultado = []
    lote = []
    for elemento in elementos:
        lote.append(elemento)
        if len(lote) == tamano:
            resultado.append(lote)
            lote = []
    if lote:
        resultado.append(lote)
    return resultado
