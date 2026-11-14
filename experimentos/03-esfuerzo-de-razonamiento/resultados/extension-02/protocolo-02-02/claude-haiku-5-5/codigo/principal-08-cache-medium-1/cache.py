"""Caché LRU con vencimiento, según TAREA.md."""

import math
from collections import OrderedDict


class Cache:
    """Caché LRU con TTL. Las entradas vencen cuando ahora >= vencimiento.

    El orden interno de `_datos` va de menos a más reciente: el primer
    elemento es el menos recientemente usado.
    """

    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero(capacidad) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_numero(ttl) or not math.isfinite(ttl) or ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento)
        self._datos = OrderedDict()
        self._hits = 0
        self._misses = 0

    # ----- auxiliares internos -----

    def _purgar(self, ahora):
        vencidas = [k for k, (_, venc) in self._datos.items() if ahora >= venc]
        for k in vencidas:
            del self._datos[k]

    def _guardar(self, clave, valor, ahora):
        """Guarda o reemplaza la entrada como la más reciente, con TTL desde `ahora`."""
        self._purgar(ahora)
        if clave in self._datos:
            del self._datos[clave]
        elif len(self._datos) >= self._capacidad:
            self._datos.popitem(last=False)  # expulsa el menos recientemente usado
        self._datos[clave] = (valor, ahora + self._ttl)

    # ----- API pública -----

    def poner(self, clave, valor):
        self._guardar(clave, valor, self._reloj())
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina.
        self._guardar(clave, valor, self._reloj())
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos.keys())

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}


def _es_entero(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)
