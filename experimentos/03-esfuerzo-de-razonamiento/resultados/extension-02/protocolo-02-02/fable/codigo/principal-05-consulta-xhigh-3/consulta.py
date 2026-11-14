from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se separa a mano (fragmento desde el primer "#", consulta desde el primer
    # "?" anterior) porque urlsplit/urlunsplit no devuelven intacto el resto:
    # pasan el esquema a minúsculas, descartan un "#" vacío y convierten
    # "x:///ruta" en "x:/ruta".
    resto, numeral, fragmento = url.partition("#")
    base, _, consulta = resto.partition("?")

    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(consulta, keep_blank_values=True)
        if clave not in cambios
    ]
    pares.extend(
        (clave, valor) for clave, valor in cambios.items() if valor is not None
    )

    nueva = urlencode(pares)
    if nueva:
        base += "?" + nueva
    return base + numeral + fragmento
