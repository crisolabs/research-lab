"""Caché LRU con vencimiento basado en un reloj inyectado."""

import math
from collections import OrderedDict


class Cache:
    """Caché de capacidad limitada con expiración fija por entrada."""

    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número finito positivo")
        if (isinstance(ttl, float) and not math.isfinite(ttl)) or ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self.capacidad = capacidad
        self.ttl = ttl
        self.reloj = reloj
        # OrderedDict conserva el orden de menos reciente a más reciente.
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [clave for clave, (_, vencimiento) in self._entradas.items()
                    if ahora >= vencimiento]
        for clave in vencidas:
            del self._entradas[clave]

    def _guardar(self, clave, valor, ahora):
        self._entradas.pop(clave, None)
        self._entradas[clave] = (valor, ahora + self.ttl)
        if len(self._entradas) > self.capacidad:
            self._entradas.popitem(last=False)

    def poner(self, clave, valor):
        ahora = self.reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        ahora = self.reloj()
        self._purgar(ahora)
        if clave not in self._entradas:
            self._misses += 1
            return defecto
        valor, vencimiento = self._entradas.pop(clave)
        self._entradas[clave] = (valor, vencimiento)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        ahora = self.reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            valor, vencimiento = self._entradas.pop(clave)
            self._entradas[clave] = (valor, vencimiento)
            self._hits += 1
            return valor
        self._misses += 1
        valor = fabrica()
        # El TTL comienza una vez que la fábrica termina.
        ahora = self.reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        ahora = self.reloj()
        self._purgar(ahora)
        return self._entradas.pop(clave, None) is not None

    def claves(self):
        ahora = self.reloj()
        self._purgar(ahora)
        return list(self._entradas.keys())

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
