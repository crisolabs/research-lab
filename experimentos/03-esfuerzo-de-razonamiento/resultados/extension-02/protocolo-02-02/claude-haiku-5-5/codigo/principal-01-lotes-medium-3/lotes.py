def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("el tamaño debe ser un int positivo")

    resultado = []
    lote_actual = []
    for elemento in elementos:
        lote_actual.append(elemento)
        if len(lote_actual) == tamano:
            resultado.append(lote_actual)
            lote_actual = []
    if lote_actual:
        resultado.append(lote_actual)
    return resultado
