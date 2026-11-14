def lotes(elementos, tamano):
    if isinstance(tamano, bool) or not isinstance(tamano, int) or tamano <= 0:
        raise ValueError("tamano debe ser un int positivo")
    resultado = []
    actual = []
    for elemento in elementos:
        actual.append(elemento)
        if len(actual) == tamano:
            resultado.append(actual)
            actual = []
    if actual:
        resultado.append(actual)
    return resultado
