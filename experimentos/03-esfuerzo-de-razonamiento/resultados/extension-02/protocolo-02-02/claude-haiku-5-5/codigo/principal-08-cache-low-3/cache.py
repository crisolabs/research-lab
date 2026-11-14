"""Caché LRU con vencimiento basada en un reloj inyectado."""

import math
from collections import OrderedDict


def _es_numero_real(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


class Cache:
    """Caché LRU donde cada entrada vence tras un TTL renovable por `poner`."""

    def __init__(self, capacidad, ttl, reloj):
        if not (isinstance(capacidad, int) and not isinstance(capacidad, bool)) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_numero_real(ttl) or not math.isfinite(ttl) or ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el primero es el menos reciente.
        self._datos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._datos.items() if ahora >= venc]
        for k in vencidas:
            del self._datos[k]

    def _guardar(self, clave, valor, ahora):
        self._purgar(ahora)
        if clave in self._datos:
            del self._datos[clave]
        elif len(self._datos) >= self._capacidad:
            self._datos.popitem(last=False)
        self._datos[clave] = (valor, ahora + self._ttl)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave][0]
        self._misses += 1
        valor = fabrica()  # si lanza, la excepción se propaga sin guardar nada
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
