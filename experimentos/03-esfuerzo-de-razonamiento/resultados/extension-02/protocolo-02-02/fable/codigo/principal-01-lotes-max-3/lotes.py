def lotes(elementos, tamano):
    # bool es subclase de int, por eso se descarta aparte. Se valida antes de
    # tocar `elementos` para no consumir un iterador si el tamaño es inválido.
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
