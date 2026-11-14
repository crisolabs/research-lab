"""Caché LRU con vencimiento por TTL y reloj inyectado."""

import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número finito positivo")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        if ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, ordenado de menos a más recientemente usada.
        self._valores = OrderedDict()
        # clave -> vencimiento, ordenado de vencimiento más cercano a más lejano
        # (TTL constante y reloj no decreciente: orden de escritura).
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencimientos = self._vencimientos
        while vencimientos:
            clave, vence = next(iter(vencimientos.items()))
            if ahora < vence:
                break
            del vencimientos[clave]
            del self._valores[clave]

    def _guardar(self, clave, valor, ahora):
        if clave in self._valores:
            del self._valores[clave]
            del self._vencimientos[clave]
        elif len(self._valores) >= self._capacidad:
            vieja, _ = self._valores.popitem(last=False)
            del self._vencimientos[vieja]
        self._valores[clave] = valor
        self._vencimientos[clave] = ahora + self._ttl

    def poner(self, clave, valor):
        hash(clave)
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._valores:
            self._valores.move_to_end(clave)
            self._hits += 1
            return self._valores[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._valores:
            self._valores.move_to_end(clave)
            self._hits += 1
            return self._valores[clave]
        self._misses += 1
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._valores:
            del self._valores[clave]
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
