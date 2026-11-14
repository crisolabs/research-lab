from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Separar manualmente para conservar intactos esquema, autoridad, ruta y
    # fragmento (urlsplit/urlunsplit normalizan el esquema, pierden "//" con
    # autoridad vacía y descartan un "#" con fragmento vacío).
    resto, almohadilla, fragmento = url.partition("#")
    prefijo, _, consulta = resto.partition("?")

    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(consulta, keep_blank_values=True)
        if clave not in cambios
    ]
    for clave, valor in cambios.items():
        if valor is not None:
            pares.append((clave, valor))

    nueva = urlencode(pares)
    resultado = prefijo
    if nueva:
        resultado += "?" + nueva
    return resultado + almohadilla + fragmento
