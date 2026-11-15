"""Caché LRU con vencimiento por TTL y reloj inyectado."""

import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número positivo y finito")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser un número positivo y finito")
        if ttl <= 0:
            raise ValueError("ttl debe ser un número positivo y finito")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, ordenado de menos a más recientemente usada.
        self._valores = OrderedDict()
        # clave -> vencimiento, ordenado por momento de escritura. Como el TTL
        # es fijo y el reloj no retrocede, también queda ordenado por
        # vencimiento, así que las vencidas están siempre al principio.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencimientos = self._vencimientos
        while vencimientos:
            clave = next(iter(vencimientos))
            if ahora < vencimientos[clave]:
                break
            del vencimientos[clave]
            del self._valores[clave]

    def _guardar(self, clave, valor, ahora):
        try:
            vencimiento = ahora + self._ttl
        except OverflowError:
            vencimiento = math.inf

        if clave in self._valores:
            self._valores[clave] = valor
            self._valores.move_to_end(clave)
            self._vencimientos[clave] = vencimiento
            self._vencimientos.move_to_end(clave)
            return

        while len(self._valores) >= self._capacidad:
            vieja, _ = self._valores.popitem(last=False)
            del self._vencimientos[vieja]
        self._valores[clave] = valor
        self._vencimientos[clave] = vencimiento

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._valores.move_to_end(clave)
            self._hits += 1
            return self._valores[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._valores:
            self._valores.move_to_end(clave)
            self._hits += 1
            return self._valores[clave]
        self._misses += 1

        # Si la fábrica lanza, la excepción se propaga sin tocar el estado.
        valor = fabrica()

        # El reloj pudo avanzar: se purga de nuevo antes de hacer lugar, para
        # no desalojar una entrada viva si alguna vencida ya liberó espacio.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._valores:
            del self._valores[clave]
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
