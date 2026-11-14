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
        # clave -> (valor, vencimiento); orden: de menos a más recientemente usada.
        self._datos = OrderedDict()
        # clave -> vencimiento; orden: de escritura más vieja a más nueva.
        # Como el reloj no decrece y el ttl es fijo, también queda ordenado
        # por vencimiento, lo que permite purgar desde el frente.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        venc = self._vencimientos
        while venc:
            clave = next(iter(venc))
            if ahora < venc[clave]:
                break
            del venc[clave]
            del self._datos[clave]

    def _guardar(self, clave, valor, ahora):
        vencimiento = ahora + self._ttl
        if clave in self._datos:
            del self._datos[clave]
            del self._vencimientos[clave]
        elif len(self._datos) >= self._capacidad:
            vieja, _ = self._datos.popitem(last=False)
            del self._vencimientos[vieja]
        self._datos[clave] = (valor, vencimiento)
        self._vencimientos[clave] = vencimiento

    def poner(self, clave, valor):
        hash(clave)
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        hash(clave)
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _FALTA)
        if entrada is _FALTA:
            self._misses += 1
            return defecto
        self._datos.move_to_end(clave)
        self._hits += 1
        return entrada[0]

    def obtener_o_crear(self, clave, fabrica):
        hash(clave)
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _FALTA)
        if entrada is not _FALTA:
            self._datos.move_to_end(clave)
            self._hits += 1
            return entrada[0]
        self._misses += 1
        valor = fabrica()  # si lanza, se propaga sin tocar el estado
        # El reloj pudo avanzar: el TTL arranca ahora y otras entradas
        # pueden haber vencido (no deben contarse al buscar espacio).
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        hash(clave)
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
