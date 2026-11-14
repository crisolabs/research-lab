from urllib.parse import urlsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    pares = parse_qsl(urlsplit(url).query, keep_blank_values=True)
    pares = [(clave, valor) for clave, valor in pares if clave not in cambios]
    pares += [(clave, valor) for clave, valor in cambios.items() if valor is not None]
    consulta = urlencode(pares)
    # La consulta se reemplaza sobre el texto original: urlunsplit no siempre
    # devuelve igual el esquema, la autoridad, la ruta o el fragmento.
    resto, numeral, fragmento = url.partition("#")
    base = resto.partition("?")[0]
    if consulta:
        base += "?" + consulta
    return base + numeral + fragmento
