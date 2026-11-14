"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_capacidad_valida(capacidad):
    return isinstance(capacidad, int) and not isinstance(capacidad, bool) and capacidad > 0


def _es_ttl_valido(ttl):
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        return False
    if isinstance(ttl, float) and not math.isfinite(ttl):
        return False
    return ttl > 0


class Cache:
    """Caché LRU con vencimiento por TTL, usando un reloj inyectado."""

    def __init__(self, capacidad, ttl, reloj):
        if not _es_capacidad_valida(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_ttl_valido(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden va de menos a más reciente.
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._entradas.items() if ahora >= venc]
        for k in vencidas:
            del self._entradas[k]

    def _guardar(self, clave, valor, ahora):
        # Reemplazo: se quita la entrada previa para que quede como la más reciente.
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            # Todas las entradas son vivas (ya purgadas): expulsa la menos reciente.
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    def _leer_viva(self, clave):
        self._entradas.move_to_end(clave)
        return self._entradas[clave][0]

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._entradas:
            self._hits += 1
            return self._leer_viva(clave)
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._entradas:
            self._hits += 1
            return self._leer_viva(clave)
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina; el reloj pudo avanzar.
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
        return list(self._entradas)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
