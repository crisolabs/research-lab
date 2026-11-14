"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _es_real_positivo_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return math.isfinite(valor) and valor > 0


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_real_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden va de menos a más reciente.
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._entradas.items() if ahora >= venc]
        for k in vencidas:
            del self._entradas[k]

    def _guardar(self, clave, valor, ahora):
        self._purgar(ahora)
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    def poner(self, clave, valor):
        self._guardar(clave, valor, self._reloj())
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._entradas:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return self._entradas[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._entradas:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return self._entradas[clave][0]
        self._misses += 1
        valor = fabrica()
        self._guardar(clave, valor, self._reloj())
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._entradas:
            del self._entradas[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._entradas.keys())

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
