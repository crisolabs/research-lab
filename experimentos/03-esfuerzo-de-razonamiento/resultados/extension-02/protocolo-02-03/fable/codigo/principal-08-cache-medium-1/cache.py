"""Caché LRU con vencimiento (TTL) basado en un reloj inyectado."""

import math
from collections import OrderedDict

_FALTA = object()


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número finito positivo")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        if ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, ordenado de menos a más recientemente usada.
        self._datos = OrderedDict()
        # clave -> vencimiento, ordenado por momento de escritura. Como el
        # reloj no decrece y el ttl es fijo, también queda ordenado por
        # vencimiento no decreciente.
        self._venc = OrderedDict()
        self._hits = 0
        self._misses = 0

    # --- internos ---------------------------------------------------------

    def _purgar(self, ahora):
        venc = self._venc
        while venc:
            clave = next(iter(venc))
            if ahora >= venc[clave]:
                del venc[clave]
                del self._datos[clave]
            else:
                break

    def _guardar(self, clave, valor, ahora):
        try:
            vencimiento = ahora + self._ttl
        except OverflowError:
            vencimiento = math.inf
        if clave in self._datos:
            self._datos[clave] = valor
            self._datos.move_to_end(clave)
        else:
            while len(self._datos) >= self._capacidad:
                vieja, _ = self._datos.popitem(last=False)
                del self._venc[vieja]
            self._datos[clave] = valor
        self._venc[clave] = vencimiento
        self._venc.move_to_end(clave)

    # --- API --------------------------------------------------------------

    def poner(self, clave, valor):
        hash(clave)
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        hash(clave)
        self._purgar(self._reloj())
        valor = self._datos.get(clave, _FALTA)
        if valor is _FALTA:
            self._misses += 1
            return defecto
        self._datos.move_to_end(clave)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        hash(clave)
        self._purgar(self._reloj())
        valor = self._datos.get(clave, _FALTA)
        if valor is not _FALTA:
            self._datos.move_to_end(clave)
            self._hits += 1
            return valor
        self._misses += 1
        valor = fabrica()
        # El reloj pudo avanzar durante la fábrica: purgar de nuevo antes de
        # desalojar, para no eliminar una entrada viva si alguna ya venció.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            del self._venc[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
