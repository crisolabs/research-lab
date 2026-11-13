def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    importe = texto.strip()
    if not importe:
        raise ValueError("formato de importe inválido")

    signo = 1
    if importe[0] in "+-":
        if importe[0] == "-":
            signo = -1
        importe = importe[1:]

    entero, separador, fraccion = importe.partition(",")
    if not entero or any(digito < "0" or digito > "9" for digito in entero):
        raise ValueError("formato de importe inválido")
    if separador and (
        not 1 <= len(fraccion) <= 2
        or any(digito < "0" or digito > "9" for digito in fraccion)
    ):
        raise ValueError("formato de importe inválido")

    unidades = 0
    for digito in entero:
        unidades = unidades * 10 + ord(digito) - ord("0")

    centavos_fraccion = 0
    if separador:
        centavos_fraccion = (ord(fraccion[0]) - ord("0")) * 10
        if len(fraccion) == 2:
            centavos_fraccion += ord(fraccion[1]) - ord("0")

    return signo * (unidades * 100 + centavos_fraccion)
