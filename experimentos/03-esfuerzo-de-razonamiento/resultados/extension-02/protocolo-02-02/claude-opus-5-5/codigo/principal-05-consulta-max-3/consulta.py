from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se separa el texto tal cual (urlsplit/urlunsplit normalizan: pasan el
    # esquema a minúsculas, descartan un '#' vacío o una autoridad vacía...).
    # El fragmento empieza en el primer '#' y la consulta en el primer '?'
    # anterior; lo que queda antes es esquema, autoridad y ruta.
    sin_fragmento, numeral, fragmento = url.partition("#")
    base, _, consulta = sin_fragmento.partition("?")

    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(consulta, keep_blank_values=True)
        if clave not in cambios
    ]
    pares.extend(
        (clave, valor) for clave, valor in cambios.items() if valor is not None
    )

    consulta = urlencode(pares)
    if consulta:
        base += "?" + consulta
    return base + numeral + fragmento
