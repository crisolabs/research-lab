"""Caché LRU con vencimiento basado en un reloj inyectado."""

from collections import OrderedDict
import math


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número positivo y finito")
        if ttl <= 0 or (isinstance(ttl, float) and not math.isfinite(ttl)):
            raise ValueError("ttl debe ser un número positivo y finito")

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

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._entradas.pop(clave, None)
        if len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar(ahora)
        try:
            valor, vencimiento = self._entradas.pop(clave)
        except KeyError:
            self._misses += 1
            return defecto
        self._entradas[clave] = (valor, vencimiento)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        try:
            valor, vencimiento = self._entradas.pop(clave)
        except KeyError:
            self._misses += 1
            valor = fabrica()
            ahora = self._reloj()
            self._purgar(ahora)
            if len(self._entradas) >= self._capacidad:
                self._entradas.popitem(last=False)
            self._entradas[clave] = (valor, ahora + self._ttl)
            return valor
        self._entradas[clave] = (valor, vencimiento)
        self._hits += 1
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar(ahora)
        return self._entradas.pop(clave, None) is not None

    def claves(self):
        ahora = self._reloj()
        self._purgar(ahora)
        return list(self._entradas)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
