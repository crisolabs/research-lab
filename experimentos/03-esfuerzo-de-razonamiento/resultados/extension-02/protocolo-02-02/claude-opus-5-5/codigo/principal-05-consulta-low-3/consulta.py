from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    pares = parse_qsl(partes.query, keep_blank_values=True)
    pares = [(k, v) for k, v in pares if k not in cambios]
    for clave, valor in cambios.items():
        if valor is not None:
            pares.append((clave, valor))
    return urlunsplit(partes._replace(query=urlencode(pares)))
