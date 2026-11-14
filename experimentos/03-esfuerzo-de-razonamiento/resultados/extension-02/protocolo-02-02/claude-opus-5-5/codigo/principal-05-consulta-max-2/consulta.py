from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se reemplaza sólo la consulta sobre el texto original; urlunsplit no
    # conserva tal cual el esquema, un fragmento vacío ni una autoridad vacía.
    previo, almohadilla, fragmento = url.partition('#')
    base, _, consulta = previo.partition('?')
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
        base += '?' + consulta
    return base + almohadilla + fragmento
