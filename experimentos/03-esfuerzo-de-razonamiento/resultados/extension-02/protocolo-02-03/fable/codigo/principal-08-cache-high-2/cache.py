"""Caché LRU con vencimiento por TTL y reloj inyectado."""

import math
from collections import OrderedDict


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen tras `ttl` segundos.

    El tiempo se toma únicamente de `reloj`, un callable que devuelve segundos
    no decrecientes. Una entrada vence cuando `ahora >= vencimiento`.
    """

    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        if capacidad <= 0:
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
        self._valores = OrderedDict()
        # clave -> vencimiento, ordenado por momento de escritura. Con TTL fijo
        # y reloj no decreciente, ese orden coincide con el de vencimiento, así
        # que alcanza con purgar desde el frente.
        self._vencimientos = OrderedDict()
        # Se activa si alguna vez se observa un vencimiento fuera de orden
        # (reloj que retrocede); en ese caso se purga recorriendo todo.
        self._desordenado = False
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #

    def _purgar(self, ahora):
        vencimientos = self._vencimientos
        if self._desordenado:
            for clave, vencimiento in list(vencimientos.items()):
                if ahora >= vencimiento:
                    del vencimientos[clave]
                    del self._valores[clave]
        else:
            while vencimientos:
                clave, vencimiento = next(iter(vencimientos.items()))
                if not ahora >= vencimiento:
                    break
                del vencimientos[clave]
                del self._valores[clave]
        if not vencimientos:
            self._desordenado = False

    def _guardar(self, clave, valor, ahora):
        """Guarda o reemplaza `clave`; supone que ya se purgó con `ahora`."""
        valores = self._valores
        vencimientos = self._vencimientos
        if clave not in valores and len(valores) >= self._capacidad:
            vieja, _ = valores.popitem(last=False)
            del vencimientos[vieja]

        vencimiento = ahora + self._ttl
        if vencimientos and vencimiento < next(reversed(vencimientos.values())):
            self._desordenado = True

        valores[clave] = valor
        valores.move_to_end(clave)
        vencimientos[clave] = vencimiento
        vencimientos.move_to_end(clave)

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        valores = self._valores
        if clave in valores:
            valores.move_to_end(clave)
            self._hits += 1
            return valores[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        valores = self._valores
        if clave in valores:
            valores.move_to_end(clave)
            self._hits += 1
            return valores[clave]

        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar las entradas.
        valor = fabrica()

        # El reloj pudo avanzar: el TTL arranca cuando la fábrica termina y
        # las entradas que vencieron mientras tanto no deben ocupar lugar.
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
        return {'hits': self._hits, 'misses': self._misses}
