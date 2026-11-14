"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _es_ttl_valido(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    if isinstance(valor, float) and not math.isfinite(valor):
        return False
    return valor > 0


class Cache:
    """Caché LRU con vencimiento por TTL, usando sólo el reloj inyectado."""

    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_ttl_valido(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento). El primero es el menos reciente.
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

    def _insertar(self, clave, valor, ahora):
        """Guarda o reemplaza la entrada como la más reciente, con TTL desde `ahora`.

        Requiere que las entradas vencidas ya hayan sido purgadas con `ahora`.
        """
        vencimiento = ahora + self._ttl
        if clave in self._entradas:
            self._entradas[clave] = (valor, vencimiento)
            self._entradas.move_to_end(clave)
            return
        if len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, vencimiento)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._insertar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return self._entradas[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return self._entradas[clave][0]
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina; el reloj pudo avanzar.
        ahora = self._reloj()
        self._purgar(ahora)
        self._insertar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            del self._entradas[clave]
            return True
        return False

    def claves(self):
        ahora = self._reloj()
        self._purgar(ahora)
        return list(self._entradas.keys())

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
