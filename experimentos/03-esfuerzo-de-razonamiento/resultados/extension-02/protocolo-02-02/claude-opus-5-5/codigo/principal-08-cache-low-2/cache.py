"""Caché LRU con vencimiento."""
import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad inválida")
        if (isinstance(ttl, bool) or not isinstance(ttl, (int, float))
                or not math.isfinite(ttl) or ttl <= 0):
            raise ValueError("ttl inválido")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._datos = OrderedDict()  # clave -> (valor, vencimiento)
        self._hits = 0
        self._misses = 0

    def _purgar(self):
        ahora = self._reloj()
        vencidas = [k for k, (_, v) in self._datos.items() if ahora >= v]
        for k in vencidas:
            del self._datos[k]
        return ahora

    def _guardar(self, clave, valor, ahora):
        if clave in self._datos:
            del self._datos[clave]
        while len(self._datos) >= self._capacidad:
            self._datos.popitem(last=False)
        self._datos[clave] = (valor, ahora + self._ttl)

    def poner(self, clave, valor):
        ahora = self._purgar()
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar()
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar()
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        valor = fabrica()
        ahora = self._purgar()
        self._guardar(clave, valor, ahora)
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
