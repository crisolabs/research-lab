def lotes(elementos, tamano):
    # La validación va antes de tocar `elementos`: con un tamaño inválido, un
    # iterable de una sola pasada tiene que quedar sin consumir.
    if isinstance(tamano, bool) or not isinstance(tamano, int):
        raise ValueError(
            f"tamano debe ser un int positivo, no {type(tamano).__name__}"
        )
    if tamano <= 0:
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
