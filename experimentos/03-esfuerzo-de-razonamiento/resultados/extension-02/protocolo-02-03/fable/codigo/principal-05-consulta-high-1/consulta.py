from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se recorta sólo la consulta sobre el texto original, de modo que esquema,
    # autoridad, ruta y fragmento queden exactamente como llegaron (reensamblar
    # con urlunsplit normaliza el esquema y descarta un fragmento vacío).
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
