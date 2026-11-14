from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    pares = [
        (k, v)
        for k, v in parse_qsl(partes.query, keep_blank_values=True)
        if k not in cambios
    ]
    pares.extend((k, v) for k, v in cambios.items() if v is not None)
    return urlunsplit(partes._replace(query=urlencode(pares)))
