def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    texto = texto.strip()
    if not texto:
        raise ValueError("Formato de importe inválido")

    signo = 1
    if texto[0] in "+-":
        if texto[0] == "-":
            signo = -1
        texto = texto[1:]

    partes = texto.split(",")
    if len(partes) > 2:
        raise ValueError("Formato de importe inválido")

    entero = partes[0]
    fraccion = partes[1] if len(partes) == 2 else ""
    if not entero or (len(partes) == 2 and not 1 <= len(fraccion) <= 2):
        raise ValueError("Formato de importe inválido")
    if not all("0" <= digito <= "9" for digito in entero + fraccion):
        raise ValueError("Formato de importe inválido")

    unidades = 0
    for digito in entero:
        unidades = unidades * 10 + ord(digito) - ord("0")

    centavos = unidades * 100
    if fraccion:
        centavos += (ord(fraccion[0]) - ord("0")) * 10
        if len(fraccion) == 2:
            centavos += ord(fraccion[1]) - ord("0")
    return signo * centavos
