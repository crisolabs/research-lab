def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un entero positivo")

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
