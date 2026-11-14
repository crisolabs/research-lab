from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # El fragmento empieza en el primer '#' y la consulta en el primer '?'
    # anterior a él (los mismos límites que usa urlsplit). Se reemplaza sólo
    # ese tramo en vez de recomponer con urlunsplit, que normaliza el resto:
    # pasa el esquema a minúsculas, descarta un '#' vacío o una autoridad
    # vacía y puede agregarle '//' o '/' a la ruta.
    previo, numeral, fragmento = url.partition('#')
    base, _, consulta = previo.partition('?')

    pares = [(clave, valor)
             for clave, valor in parse_qsl(consulta, keep_blank_values=True)
             if clave not in cambios]
    pares += [(clave, valor)
              for clave, valor in cambios.items()
              if valor is not None]

    consulta = urlencode(pares)
    if consulta:
        base += '?' + consulta
    return base + numeral + fragmento
