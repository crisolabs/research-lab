from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se separa a mano (igual criterio que urlsplit: primero '#', luego '?')
    # para conservar literalmente esquema, autoridad, ruta y fragmento.
    base, hay_fragmento, fragmento = url.partition('#')
    prefijo, _, consulta = base.partition('?')

    pares = parse_qsl(consulta, keep_blank_values=True)
    pares = [(clave, valor) for clave, valor in pares if clave not in cambios]
    for clave, valor in cambios.items():
        if valor is not None:
            pares.append((clave, valor))

    nueva = urlencode(pares)
    resultado = prefijo
    if nueva:
        resultado += '?' + nueva
    if hay_fragmento:
        resultado += '#' + fragmento
    return resultado
