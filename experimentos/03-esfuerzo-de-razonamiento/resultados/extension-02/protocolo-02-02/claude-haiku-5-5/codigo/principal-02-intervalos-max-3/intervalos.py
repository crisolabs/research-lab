import math


def _validar_extremo(valor):
    if isinstance(valor, bool):
        raise ValueError(f"extremo booleano no permitido: {valor!r}")
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        if not math.isfinite(valor):
            raise ValueError(f"extremo no finito: {valor!r}")
        return valor
    raise ValueError(f"extremo inválido: {valor!r}")


def _validar_intervalo(par):
    if not isinstance(par, (list, tuple)) or len(par) != 2:
        raise ValueError(f"intervalo mal formado: {par!r}")
    inicio = _validar_extremo(par[0])
    fin = _validar_extremo(par[1])
    if inicio > fin:
        raise ValueError(f"intervalo con inicio mayor que fin: {par!r}")
    return inicio, fin


def unir(intervalos):
    try:
        iterador = iter(intervalos)
    except TypeError as exc:
        raise ValueError("la entrada debe ser un iterable de intervalos") from exc

    validos = sorted(_validar_intervalo(par) for par in iterador)

    resultado = []
    for inicio, fin in validos:
        if resultado and inicio <= resultado[-1][1]:
            resultado[-1][1] = max(resultado[-1][1], fin)
        else:
            resultado.append([inicio, fin])
    return resultado
