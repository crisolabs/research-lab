"""Caché LRU con vencimiento (ver TAREA.md)."""

import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        if capacidad <= 0:
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
        self._datos = OrderedDict()
        # clave -> vencimiento, ordenado por vencimiento creciente (el TTL es
        # fijo y el reloj no decrece, así que el orden de escritura lo respeta).
        self._venc = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        venc = self._venc
        while venc:
            clave = next(iter(venc))
            if ahora >= venc[clave]:
                del venc[clave]
                del self._datos[clave]
            else:
                break

    def _guardar(self, clave, valor, ahora):
        if clave in self._datos:
            del self._venc[clave]
        elif len(self._datos) >= self._capacidad:
            vieja, _ = self._datos.popitem(last=False)
            del self._venc[vieja]
        self._datos[clave] = valor
        self._datos.move_to_end(clave)
        self._venc[clave] = ahora + self._ttl

    def poner(self, clave, valor):
        hash(clave)
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave]
        self._misses += 1
        valor = fabrica()
        # El reloj pudo avanzar durante la fábrica: se purga de nuevo antes de
        # decidir si hay que desalojar, y el TTL arranca desde este instante.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            del self._venc[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
