from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    # surrogateescape: los bytes porcentuales que no son UTF-8 válido
    # sobreviven intactos al ciclo decodificar/codificar.
    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(
            partes.query, keep_blank_values=True, errors="surrogateescape"
        )
        if clave not in cambios
    ]
    pares.extend(
        (clave, valor) for clave, valor in cambios.items() if valor is not None
    )
    consulta = urlencode(pares, errors="surrogateescape")
    return urlunsplit(partes._replace(query=consulta))
