from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    sin_fragmento, numeral, fragmento = url.partition('#')
    base, _, consulta = sin_fragmento.partition('?')
    ajenos = [
        (k, v) for k, v in parse_qsl(consulta, keep_blank_values=True)
        if k not in cambios
    ]
    nuevos = [(k, v) for k, v in cambios.items() if v is not None]
    codificada = urlencode(ajenos + nuevos)
    if codificada:
        base += '?' + codificada
    return base + numeral + fragmento
