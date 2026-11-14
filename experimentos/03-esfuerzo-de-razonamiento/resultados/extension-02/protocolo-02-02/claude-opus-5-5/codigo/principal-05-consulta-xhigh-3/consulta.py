from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Separar manualmente fragmento y consulta para conservar sin alteraciones
    # el esquema, la autoridad, la ruta y el fragmento (urlsplit/urlunsplit
    # pueden normalizar mayúsculas del esquema, descartar un "#" vacío, etc.).
    resto, almohadilla, fragmento = url.partition("#")
    base, _, consulta = resto.partition("?")

    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(consulta, keep_blank_values=True)
        if clave not in cambios
    ]
    pares.extend(
        (clave, valor) for clave, valor in cambios.items() if valor is not None
    )

    nueva = urlencode(pares)
    resultado = base
    if nueva:
        resultado += "?" + nueva
    if almohadilla:
        resultado += "#" + fragmento
    return resultado
