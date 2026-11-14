"""Caché LRU con vencimiento basada en un reloj inyectado."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return type(valor) is int and valor > 0


def _es_numero_positivo_finito(valor):
    if type(valor) not in (int, float):
        return False
    return math.isfinite(valor) and valor > 0


class Cache:
    """Caché de capacidad limitada, expiración por TTL y desalojo LRU.

    Las entradas se guardan en un OrderedDict ordenado de menos a más
    reciente; cada valor es una tupla (valor, vencimiento).
    """

    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_numero_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    # ----- internos -------------------------------------------------

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._entradas.items() if ahora >= venc]
        for k in vencidas:
            del self._entradas[k]

    def _insertar(self, clave, valor, ahora):
        # Purga primero para que las vencidas no cuenten como víctimas de LRU.
        self._purgar(ahora)
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    # ----- API pública ----------------------------------------------

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._insertar(clave, valor, ahora)
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
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        self._insertar(clave, valor, self._reloj())
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
