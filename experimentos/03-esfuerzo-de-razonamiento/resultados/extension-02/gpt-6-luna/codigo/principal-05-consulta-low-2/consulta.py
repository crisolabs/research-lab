from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    pares = parse_qsl(partes.query, keep_blank_values=True)
    claves_actualizadas = set(cambios)
    consulta = [par for par in pares if par[0] not in claves_actualizadas]
    consulta.extend((clave, valor) for clave, valor in cambios.items() if valor is not None)
    return urlunsplit(partes._replace(query=urlencode(consulta)))
