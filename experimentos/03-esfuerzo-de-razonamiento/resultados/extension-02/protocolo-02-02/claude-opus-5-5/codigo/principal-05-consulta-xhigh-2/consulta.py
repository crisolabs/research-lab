from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Separar manualmente para conservar intactos esquema, autoridad, ruta y
    # fragmento (urlunsplit pierde, p. ej., un "#" vacío o un "//" vacío).
    # Mismas reglas que urlsplit: el fragmento empieza en el primer "#" y la
    # consulta en el primer "?" anterior a él.
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
