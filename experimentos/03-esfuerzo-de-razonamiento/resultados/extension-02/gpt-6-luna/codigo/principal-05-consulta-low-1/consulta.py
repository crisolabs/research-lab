from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl


def actualizar(url, cambios):
    partes = urlsplit(url)
    consulta = dict(parse_qsl(partes.query))
    consulta.update(cambios)
    return urlunsplit(partes._replace(query=urlencode(consulta)))
