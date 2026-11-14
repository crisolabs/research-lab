from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se parte la URL a mano (el fragmento empieza en el primer '#', la consulta
    # en el primer '?' anterior) para devolver esquema, autoridad, ruta y
    # fragmento exactamente como vinieron, sin la normalización de urlunsplit.
    resto, marca_fragmento, fragmento = url.partition('#')
    base, _, consulta = resto.partition('?')

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
        base += '?' + nueva
    return base + marca_fragmento + fragmento
