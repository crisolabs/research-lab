from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    pares = parse_qsl(partes.query, keep_blank_values=True)
    claves_actualizadas = cambios.keys()
    consulta = [(clave, valor) for clave, valor in pares if clave not in claves_actualizadas]
    consulta.extend(
        (clave, valor)
        for clave, valor in cambios.items()
        if valor is not None
    )
    return urlunsplit(partes._replace(query=urlencode(consulta)))
