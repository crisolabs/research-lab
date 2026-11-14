"""Caché LRU con vencimiento sobre un reloj inyectado."""

import math
from collections import OrderedDict


def _es_capacidad_valida(capacidad):
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        return False
    return capacidad > 0


def _es_ttl_valido(ttl):
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        return False
    if isinstance(ttl, float) and not math.isfinite(ttl):
        return False
    return ttl > 0


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_capacidad_valida(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_ttl_valido(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # Claves de menos a más reciente (orden LRU).
        self._valores = OrderedDict()
        # Claves por vencimiento creciente. El reloj no decrece, así que cada
        # renovación va al final y la primera es la próxima en vencer.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave not in self._valores:
            self._misses += 1
            return defecto
        self._hits += 1
        self._valores.move_to_end(clave)
        return self._valores[clave]

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._hits += 1
            self._valores.move_to_end(clave)
            return self._valores[clave]
        self._misses += 1
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave not in self._valores:
            return False
        del self._valores[clave]
        del self._vencimientos[clave]
        return True

    def claves(self):
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}

    def _purgar(self, ahora):
        vencimientos = self._vencimientos
        while vencimientos:
            clave = next(iter(vencimientos))
            if vencimientos[clave] > ahora:
                break
            del vencimientos[clave]
            del self._valores[clave]

    def _guardar(self, clave, valor, ahora):
        if clave in self._valores:
            self._valores[clave] = valor
            self._valores.move_to_end(clave)
        else:
            if len(self._valores) >= self._capacidad:
                menos_reciente, _ = self._valores.popitem(last=False)
                del self._vencimientos[menos_reciente]
            self._valores[clave] = valor
        self._vencimientos[clave] = ahora + self._ttl
        self._vencimientos.move_to_end(clave)
