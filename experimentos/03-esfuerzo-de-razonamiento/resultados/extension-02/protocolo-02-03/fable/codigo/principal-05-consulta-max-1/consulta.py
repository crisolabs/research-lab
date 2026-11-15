from urllib.parse import parse_qsl, urlencode


def actualizar(url, cambios):
    # La consulta se recorta del texto original (entre el primer "?" y el
    # primer "#") en vez de reensamblar con urlunsplit: así esquema, autoridad,
    # ruta y fragmento vuelven tal cual, sin la normalización de urlsplit.
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
        base = f"{base}?{nueva}"
    return base + numeral + fragmento
