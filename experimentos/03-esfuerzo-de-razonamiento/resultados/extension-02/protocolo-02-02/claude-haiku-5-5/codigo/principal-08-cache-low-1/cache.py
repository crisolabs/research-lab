"""Caché LRU con vencimiento basada en un reloj inyectado."""

import math
from collections import OrderedDict


def _es_entero_positivo(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _es_numero_positivo_finito(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    return math.isfinite(v) and v > 0


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_numero_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden va de menos a más reciente.
        self._datos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self):
        ahora = self._reloj()
        vencidas = [k for k, (_, venc) in self._datos.items() if ahora >= venc]
        for k in vencidas:
            del self._datos[k]

    def _guardar(self, clave, valor):
        # Se asume que ya se purgó. Si la clave existe se reemplaza sin desalojar.
        ahora = self._reloj()
        if clave not in self._datos:
            while len(self._datos) >= self._capacidad:
                self._datos.popitem(last=False)
        self._datos[clave] = (valor, ahora + self._ttl)
        self._datos.move_to_end(clave)

    def poner(self, clave, valor):
        self._purgar()
        self._guardar(clave, valor)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar()
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar()
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave][0]
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        # El reloj pudo avanzar mientras la fábrica trabajaba.
        self._purgar()
        self._guardar(clave, valor)
        return valor

    def borrar(self, clave):
        self._purgar()
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def claves(self):
        self._purgar()
        return list(self._datos.keys())

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
