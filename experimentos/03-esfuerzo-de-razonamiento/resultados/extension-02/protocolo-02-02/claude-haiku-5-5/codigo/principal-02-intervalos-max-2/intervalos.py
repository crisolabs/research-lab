import math


def _extremo_valido(x):
    if isinstance(x, bool):
        return False
    if isinstance(x, int):
        return True
    return isinstance(x, float) and math.isfinite(x)


def _validar_intervalo(iv):
    if not isinstance(iv, (list, tuple)) or len(iv) != 2:
        raise ValueError("cada intervalo debe tener exactamente dos extremos")
    inicio, fin = iv
    if not (_extremo_valido(inicio) and _extremo_valido(fin)):
        raise ValueError("los extremos deben ser enteros o flotantes finitos")
    if inicio > fin:
        raise ValueError("el inicio de un intervalo no puede ser mayor que su fin")
    return inicio, fin


def unir(intervalos):
    pares = sorted(_validar_intervalo(iv) for iv in intervalos)
    resultado = []
    for inicio, fin in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fin > resultado[-1][1]:
                resultado[-1][1] = fin
        else:
            resultado.append([inicio, fin])
    return resultado
