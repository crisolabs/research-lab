def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un string")

    texto = texto.strip()
    if not texto:
        raise ValueError("formato de importe inválido")

    signo = 1
    if texto[0] in "+-":
        if texto[0] == "-":
            signo = -1
        texto = texto[1:]

    parte_entera, coma, parte_decimal = texto.partition(",")

    def son_digitos_ascii(parte):
        return bool(parte) and all("0" <= caracter <= "9" for caracter in parte)

    if not son_digitos_ascii(parte_entera):
        raise ValueError("formato de importe inválido")
    if coma and (not 1 <= len(parte_decimal) <= 2 or not son_digitos_ascii(parte_decimal)):
        raise ValueError("formato de importe inválido")

    centimos = 0
    for digito in parte_entera:
        centimos = centimos * 10 + ord(digito) - ord("0")
    centimos *= 100

    if coma:
        fraccion = ord(parte_decimal[0]) - ord("0")
        if len(parte_decimal) == 2:
            fraccion = fraccion * 10 + ord(parte_decimal[1]) - ord("0")
        else:
            fraccion *= 10
        centimos += fraccion

    return signo * centimos
