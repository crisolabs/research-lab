"""Caché LRU con vencimiento basada en un reloj inyectado."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return type(valor) is int and valor > 0


def _es_numero_positivo_finito(valor):
    if type(valor) not in (int, float):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return valor > 0


class Cache:
    """Caché de capacidad fija, con recencia LRU y expiración por TTL.

    Las entradas vencen cuando ``ahora >= vencimiento``. ``poner`` renueva el
    TTL; las lecturas sólo actualizan la recencia.
    """

    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_numero_positivo_finito(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento); el orden va de menos a más reciente.
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [
            clave
            for clave, (_, venc) in self._entradas.items()
            if ahora >= venc
        ]
        for clave in vencidas:
            del self._entradas[clave]

    def _insertar(self, clave, valor, ahora):
        """Guarda o reemplaza una entrada ya purgada, respetando la capacidad."""
        if clave in self._entradas:
            del self._entradas[clave]
        elif len(self._entradas) >= self._capacidad:
            # Todas las entradas están vivas (ya purgadas): expulsa la menos reciente.
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, ahora + self._ttl)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._insertar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._entradas:
            self._hits += 1
            self._entradas.move_to_end(clave)
            return self._entradas[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            self._hits += 1
            self._entradas.move_to_end(clave)
            return self._entradas[clave][0]
        self._misses += 1
        # La fábrica no llama al caché; si lanza, la excepción se propaga
        # sin tocar las entradas existentes.
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._insertar(clave, valor, ahora)
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
