def lotes(elementos, tamano):
    if type(tamano) is not int or tamano <= 0:
        raise ValueError("el tamaño debe ser un int positivo")

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
