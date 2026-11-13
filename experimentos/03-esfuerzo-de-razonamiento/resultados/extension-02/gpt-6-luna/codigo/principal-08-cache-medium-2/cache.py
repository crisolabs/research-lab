"""Caché LRU con vencimiento basado en un reloj inyectado."""

from collections import OrderedDict
import math


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if (
            isinstance(ttl, bool)
            or not isinstance(ttl, (int, float))
            or ttl <= 0
            or (isinstance(ttl, float) and not math.isfinite(ttl))
        ):
            raise ValueError("ttl debe ser un número finito positivo")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [
            clave
            for clave, (_, vencimiento) in self._entradas.items()
            if ahora >= vencimiento
        ]
        for clave in vencidas:
            del self._entradas[clave]

    def _guardar(self, clave, valor, ahora):
        vencimiento = ahora + self._ttl
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, vencimiento)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar(ahora)
        try:
            valor, vencimiento = self._entradas[clave]
        except KeyError:
            self._misses += 1
            return defecto
        self._entradas.move_to_end(clave)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        try:
            valor, vencimiento = self._entradas[clave]
        except KeyError:
            self._misses += 1
            valor = fabrica()
            ahora = self._reloj()
            self._purgar(ahora)
            self._guardar(clave, valor, ahora)
            return valor
        self._entradas.move_to_end(clave)
        self._hits += 1
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar(ahora)
        try:
            del self._entradas[clave]
        except KeyError:
            return False
        return True

    def claves(self):
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
