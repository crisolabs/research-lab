from urllib.parse import urlencode, parse_qsl


def actualizar(url, cambios):
    # Se recorta la consulta a mano (en vez de urlsplit/urlunsplit) para que
    # esquema, autoridad, ruta y fragmento queden exactamente como estaban.
    resto, numeral, fragmento = url.partition("#")
    base, _, consulta = resto.partition("?")

    # surrogateescape: los bytes percent-codificados que no son UTF-8 válido
    # en claves ajenas sobreviven el ciclo decodificar/codificar.
    pares = [
        (clave, valor)
        for clave, valor in parse_qsl(
            consulta, keep_blank_values=True, errors="surrogateescape"
        )
        if clave not in cambios
    ]
    pares.extend(
        (clave, valor) for clave, valor in cambios.items() if valor is not None
    )

    nueva = urlencode(pares, errors="surrogateescape")
    return base + ("?" + nueva if nueva else "") + numeral + fragmento
