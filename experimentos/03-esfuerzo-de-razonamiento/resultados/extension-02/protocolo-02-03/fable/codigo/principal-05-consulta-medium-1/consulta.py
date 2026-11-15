from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se separa a mano para conservar literalmente esquema, autoridad, ruta
    # y fragmento (urlsplit/urlunsplit normalizan algunos casos).
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
