import math
from numbers import Real


def unir(intervalos):
    pares = []
    try:
        for intervalo in intervalos:
            if isinstance(intervalo, (str, bytes)):
                raise ValueError
            extremos = list(intervalo)
            if len(extremos) != 2:
                raise ValueError
            inicio, fin = extremos
            if (
                isinstance(inicio, bool)
                or isinstance(fin, bool)
                or not isinstance(inicio, Real)
                or not isinstance(fin, Real)
                or not math.isfinite(inicio)
                or not math.isfinite(fin)
                or inicio > fin
            ):
                raise ValueError
            pares.append((inicio, fin))
    except (TypeError, OverflowError) as error:
        raise ValueError("intervalos mal formados") from error

    pares.sort(key=lambda par: (par[0], par[1]))
    unidos = []
    for inicio, fin in pares:
        if unidos and inicio <= unidos[-1][1]:
            if fin > unidos[-1][1]:
                unidos[-1][1] = fin
        else:
            unidos.append([inicio, fin])
    return unidos
