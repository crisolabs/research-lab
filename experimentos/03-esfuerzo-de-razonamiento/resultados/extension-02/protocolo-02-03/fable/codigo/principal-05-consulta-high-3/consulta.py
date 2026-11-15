from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se separa la consulta a mano (igual que urlsplit: el fragmento empieza en
    # el primer '#', la consulta en el primer '?' anterior) para devolver el
    # resto de la URL tal cual, sin la normalización de urlunsplit.
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
