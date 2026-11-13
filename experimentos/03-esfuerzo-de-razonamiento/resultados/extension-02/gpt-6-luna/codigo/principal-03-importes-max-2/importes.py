import re


def centavos(texto):
    if not isinstance(texto, str):
        raise ValueError("el importe debe ser un texto")

    importe = texto.strip()
    if re.fullmatch(r"[+-]?[0-9]+(?:,[0-9]{1,2})?", importe) is None:
        raise ValueError("formato de importe inválido")

    signo = 1
    if importe[0] in "+-":
        if importe[0] == "-":
            signo = -1
        importe = importe[1:]

    partes = importe.split(",", 1)
    entero = partes[0]
    fraccion = partes[1] if len(partes) == 2 else ""
    fraccion = (fraccion + "00")[:2]

    unidades = 0
    for inicio in range(0, len(entero), 9):
        bloque = entero[inicio:inicio + 9]
        valor_bloque = 0
        for digito in bloque:
            valor_bloque = valor_bloque * 10 + ord(digito) - ord("0")
        unidades = unidades * (10 ** len(bloque)) + valor_bloque

    centimos = 0
    for digito in fraccion:
        centimos = centimos * 10 + ord(digito) - ord("0")

    return signo * (unidades * 100 + centimos)
