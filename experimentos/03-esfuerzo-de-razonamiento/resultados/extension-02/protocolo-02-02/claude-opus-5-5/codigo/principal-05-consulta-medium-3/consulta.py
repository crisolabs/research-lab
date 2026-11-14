from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Separar fragmento y consulta sin alterar el resto de la URL
    # (esquema, autoridad y ruta se conservan textualmente).
    base, sep_frag, fragmento = url.partition("#")
    prefijo, sep_query, query = base.partition("?")

    pares = parse_qsl(query, keep_blank_values=True)
    pares = [(k, v) for k, v in pares if k not in cambios]
    for clave, valor in cambios.items():
        if valor is not None:
            pares.append((clave, valor))

    nueva = urlencode(pares)
    resultado = prefijo
    if nueva:
        resultado += "?" + nueva
    if sep_frag:
        resultado += "#" + fragmento
    return resultado
