def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("El importe debe ser un string")

    importe = texto.strip()
    signo = 1
    if importe.startswith(("+", "-")):
        if importe[0] == "-":
            signo = -1
        importe = importe[1:]

    entero, separador, decimal = importe.partition(",")
    if (
        not entero
        or any(digito not in "0123456789" for digito in entero)
        or (
            separador
            and (
                len(decimal) not in (1, 2)
                or any(digito not in "0123456789" for digito in decimal)
            )
        )
    ):
        raise ValueError("Formato de importe inválido")

    resultado = 0
    for digito in entero:
        resultado = resultado * 10 + ord(digito) - ord("0")
    resultado *= 100
    if decimal:
        resultado += (ord(decimal[0]) - ord("0")) * 10
        if len(decimal) == 2:
            resultado += ord(decimal[1]) - ord("0")
    return signo * resultado
