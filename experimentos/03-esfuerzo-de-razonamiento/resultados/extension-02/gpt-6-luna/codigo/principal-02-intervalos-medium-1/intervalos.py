import math


def unir(intervalos):
    """Une intervalos cerrados que se superponen o se tocan."""
    try:
        pares = []
        for intervalo in intervalos:
            try:
                par = list(intervalo)
            except (TypeError, ValueError):
                raise ValueError("cada intervalo debe contener dos extremos") from None

            if len(par) != 2:
                raise ValueError("cada intervalo debe contener dos extremos")

            inicio, fin = par
            for extremo in par:
                if isinstance(extremo, bool) or not isinstance(extremo, (int, float)):
                    raise ValueError("los extremos deben ser números finitos")
                if isinstance(extremo, float) and not math.isfinite(extremo):
                    raise ValueError("los extremos deben ser números finitos")

            if inicio > fin:
                raise ValueError("el inicio no puede ser mayor que el fin")
            pares.append([inicio, fin])
    except (TypeError, ValueError, OverflowError) as error:
        if isinstance(error, ValueError):
            raise
        raise ValueError("entrada de intervalos inválida") from None

    pares.sort(key=lambda par: par[0])
    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
