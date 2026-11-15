"""Caché LRU con vencimiento (TTL) y reloj inyectado."""

import heapq
import math
from collections import OrderedDict
from fractions import Fraction
from itertools import count

_AUSENTE = object()


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen `ttl` segundos después de guardarse.

    El tiempo sale únicamente de `reloj`, un callable que devuelve segundos no
    decrecientes. Una entrada vence cuando `ahora >= vencimiento`; las lecturas
    actualizan la recencia pero no renuevan el vencimiento.
    """

    def __init__(self, capacidad, ttl, reloj):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if (
            isinstance(ttl, bool)
            or not isinstance(ttl, (int, float))
            or (isinstance(ttl, float) and not math.isfinite(ttl))
            or ttl <= 0
        ):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento, serie), de menos a más recientemente usada.
        self._entradas = OrderedDict()
        # Montículo de (vencimiento, serie, clave). Puede contener registros
        # obsoletos (de entradas reemplazadas o eliminadas), reconocibles porque
        # su serie ya no coincide con la de la entrada vigente.
        self._monton = []
        self._series = count()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        entrada = self._leer(clave)
        return defecto if entrada is None else entrada[0]

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        entrada = self._leer(clave)
        if entrada is not None:
            return entrada[0]
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina, y mientras trabajaba pueden
        # haber vencido otras entradas: se purgan antes de desalojar una viva.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        return self._entradas.pop(clave, _AUSENTE) is not _AUSENTE

    def claves(self):
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}

    def _leer(self, clave):
        """Devuelve la entrada viva de `clave` (o None) y contabiliza hit o miss."""
        entrada = self._entradas.get(clave)
        if entrada is None:
            self._misses += 1
        else:
            self._entradas.move_to_end(clave)
            self._hits += 1
        return entrada

    def _purgar(self, ahora):
        """Elimina todas las entradas con `vencimiento <= ahora`."""
        monton = self._monton
        entradas = self._entradas
        while monton and monton[0][0] <= ahora:
            _, serie, clave = heapq.heappop(monton)
            entrada = entradas.get(clave)
            if entrada is not None and entrada[2] == serie:
                del entradas[clave]

    def _guardar(self, clave, valor, ahora):
        """Guarda o reemplaza `clave` como la más reciente; las vencidas ya se purgaron."""
        entradas = self._entradas
        vencimiento = self._vencimiento(ahora)
        if clave not in entradas and len(entradas) >= self._capacidad:
            entradas.popitem(last=False)
        serie = next(self._series)
        entradas[clave] = (valor, vencimiento, serie)
        entradas.move_to_end(clave)
        heapq.heappush(self._monton, (vencimiento, serie, clave))
        if len(self._monton) > 2 * len(entradas) + 16:
            # Demasiados registros obsoletos: se rehace sólo con los vigentes.
            self._monton = [(v, s, c) for c, (_, v, s) in entradas.items()]
            heapq.heapify(self._monton)

    def _vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except OverflowError:
            # Entero demasiado grande para un float: se suma de forma exacta.
            return Fraction(ahora) + Fraction(self._ttl)
