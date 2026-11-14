"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


def _es_entero_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _es_real_positivo_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
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
        # clave -> valor, de menos a más reciente (la primera se expulsa antes).
        self._valores = OrderedDict()
        # clave -> vencimiento, por orden de escritura. El reloj no decrece,
        # así que los vencimientos quedan ordenados y se purga desde el frente.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora + self._ttl)

    def obtener(self, clave, defecto=None):
        encontrada, valor = self._buscar(clave)
        return valor if encontrada else defecto

    def obtener_o_crear(self, clave, fabrica):
        encontrada, valor = self._buscar(clave)
        if encontrada:
            return valor
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora + self._ttl)
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
        return {'hits': self._hits, 'misses': self._misses}

    def _buscar(self, clave):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._hits += 1
            self._valores.move_to_end(clave)
            return True, self._valores[clave]
        self._misses += 1
        return False, None

    def _purgar(self, ahora):
        while self._vencimientos:
            clave = next(iter(self._vencimientos))
            if self._vencimientos[clave] > ahora:
                break
            del self._vencimientos[clave]
            del self._valores[clave]

    def _guardar(self, clave, valor, vencimiento):
        if clave in self._valores:
            del self._valores[clave]
            del self._vencimientos[clave]
        elif len(self._valores) >= self._capacidad:
            menos_reciente = next(iter(self._valores))
            del self._valores[menos_reciente]
            del self._vencimientos[menos_reciente]
        self._valores[clave] = valor
        self._vencimientos[clave] = vencimiento
