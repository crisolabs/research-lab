"""Implementá la caché pedida en TAREA.md."""

import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_entero_positivo(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_ttl_valido(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, de menos a más reciente
        self._valores = OrderedDict()
        # clave -> vencimiento; como el reloj no retrocede, este orden también es el de vencimiento
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        vencimiento = ahora + self._ttl
        if clave in self._valores:
            self._quitar(clave)
        if vencimiento <= ahora:
            # ttl tan chico que ahora + ttl == ahora por redondeo: la entrada nace vencida
            return None
        if len(self._valores) >= self._capacidad:
            self._quitar(next(iter(self._valores)))
        self._valores[clave] = valor
        self._vencimientos[clave] = vencimiento
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._hits += 1
            self._valores.move_to_end(clave)
            return self._valores[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._hits += 1
            self._valores.move_to_end(clave)
            return self._valores[clave]
        self._misses += 1
        valor = fabrica()
        # poner relee el reloj: el TTL arranca cuando la fábrica termina
        self.poner(clave, valor)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._quitar(clave)
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}

    def _purgar(self, ahora):
        while self._vencimientos:
            clave = next(iter(self._vencimientos))
            if self._vencimientos[clave] > ahora:
                break
            self._quitar(clave)

    def _quitar(self, clave):
        del self._valores[clave]
        del self._vencimientos[clave]


def _es_entero_positivo(x):
    return isinstance(x, int) and not isinstance(x, bool) and x > 0


def _es_ttl_valido(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    try:
        return math.isfinite(x) and x > 0
    except OverflowError:
        return False
