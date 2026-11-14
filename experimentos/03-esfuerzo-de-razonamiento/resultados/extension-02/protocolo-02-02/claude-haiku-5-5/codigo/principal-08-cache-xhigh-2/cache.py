"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _es_real_positivo_finito(valor):
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return valor > 0


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_real_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden va de menos a más reciente.
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [c for c, (_, venc) in self._entradas.items() if ahora >= venc]
        for clave in vencidas:
            del self._entradas[clave]

    def _guardar(self, clave, valor, ahora):
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            # Tras purgar, todas las entradas son vivas: sale la menos reciente.
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
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
        # Si la fábrica lanza, la excepción sale sin tocar las entradas.
        valor = fabrica()
        # El TTL arranca cuando la fábrica termina; el reloj pudo avanzar.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
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
