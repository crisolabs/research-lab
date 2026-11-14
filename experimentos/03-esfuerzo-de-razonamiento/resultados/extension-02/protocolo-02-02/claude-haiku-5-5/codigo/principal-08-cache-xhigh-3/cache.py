"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_entero_positivo(x):
    return isinstance(x, int) and not isinstance(x, bool) and x > 0


def _es_real_positivo_finito(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    if isinstance(x, float) and not math.isfinite(x):
        return False
    return x > 0


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_real_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden es de menos a más reciente.
        self._datos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        self._guardar(clave, valor, self._reloj())
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        valor = fabrica()
        self._guardar(clave, valor, self._reloj())
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos.keys())

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._datos.items() if ahora >= venc]
        for k in vencidas:
            del self._datos[k]

    def _guardar(self, clave, valor, ahora):
        self._purgar(ahora)
        if clave in self._datos:
            self._datos.move_to_end(clave)
        elif len(self._datos) >= self._capacidad:
            self._datos.popitem(last=False)
        self._datos[clave] = (valor, ahora + self._ttl)
