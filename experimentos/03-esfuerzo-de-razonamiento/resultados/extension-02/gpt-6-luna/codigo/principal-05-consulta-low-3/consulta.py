from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    consulta = parse_qsl(partes.query, keep_blank_values=True)
    claves_a_actualizar = cambios.keys()
    consulta = [(clave, valor) for clave, valor in consulta if clave not in claves_a_actualizar]
    consulta.extend((clave, valor) for clave, valor in cambios.items() if valor is not None)
    return urlunsplit(partes._replace(query=urlencode(consulta)))
