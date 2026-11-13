def centavos(texto):
    return int(float(texto.replace(",", ".")) * 100)
