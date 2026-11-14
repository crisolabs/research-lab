from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # La URL se corta a mano según RFC 3986 (el fragmento empieza en el primer
    # "#" y la consulta en el primer "?" anterior a él) para devolver intacto
    # todo lo que no es consulta: urlsplit/urlunsplit pasan el esquema a
    # minúsculas, descartan un "#" vacío y reescriben autoridades vacías
    # ("foo:///a" -> "foo:/a").
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
