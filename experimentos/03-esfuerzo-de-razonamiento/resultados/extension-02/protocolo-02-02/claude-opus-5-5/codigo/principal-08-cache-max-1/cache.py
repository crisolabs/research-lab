"""Caché LRU con vencimiento por TTL medido con un reloj inyectado."""

import math
import numbers
from collections import OrderedDict
from fractions import Fraction

_AUSENTE = object()


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen ``ttl`` segundos
    después de su última escritura, según ``reloj()``."""

    def __init__(self, capacidad, ttl, reloj):
        if (not isinstance(capacidad, int) or isinstance(capacidad, bool)
                or capacidad <= 0):
            raise ValueError(
                f"capacidad debe ser un entero positivo, no {capacidad!r}")
        if (not isinstance(ttl, (int, float)) or isinstance(ttl, bool)
                or (isinstance(ttl, float) and not math.isfinite(ttl))
                or ttl <= 0):
            raise ValueError(
                f"ttl debe ser un número finito positivo, no {ttl!r}")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, de menos a más recientemente usada.
        self._valores = OrderedDict()
        # clave -> vencimiento, en orden de última escritura. Como el TTL es
        # fijo y el reloj no decrece, también es el orden de vencimiento, así
        # que las vencidas siempre forman un prefijo.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        """Guarda o reemplaza ``valor`` con TTL nuevo y lo marca como el más
        reciente; si no hay lugar expulsa la entrada viva menos reciente."""
        self._guardar(clave, valor, self._reloj())

    def obtener(self, clave, defecto=None):
        """Devuelve el valor vivo de ``clave`` (sin renovar su TTL) o
        ``defecto``, sumando un hit o un miss."""
        self._purgar(self._reloj())
        valor = self._valores.get(clave, _AUSENTE)
        if valor is _AUSENTE:
            self._misses += 1
            return defecto
        self._valores.move_to_end(clave)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        """Como ``obtener``, pero si la clave no está guarda y devuelve
        ``fabrica()``. Si la fábrica lanza, el caché no pierde entradas
        vivas."""
        self._purgar(self._reloj())
        valor = self._valores.get(clave, _AUSENTE)
        if valor is not _AUSENTE:
            self._valores.move_to_end(clave)
            self._hits += 1
            return valor
        self._misses += 1
        valor = fabrica()
        # El reloj pudo avanzar mientras trabajaba la fábrica: el TTL empieza
        # ahora, y la expulsión se decide recién ahora, con las entradas que
        # sigan vivas.
        self._guardar(clave, valor, self._reloj())
        return valor

    def borrar(self, clave):
        """Elimina ``clave`` si está viva; devuelve si la eliminó."""
        self._purgar(self._reloj())
        if clave not in self._valores:
            return False
        del self._valores[clave]
        del self._vencimientos[clave]
        return True

    def claves(self):
        """Devuelve una lista nueva con las claves vivas, de menos a más
        reciente."""
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        """Devuelve una copia de los contadores de hits y misses."""
        return {'hits': self._hits, 'misses': self._misses}

    def _guardar(self, clave, valor, ahora):
        vencimiento = self._vencimiento(ahora)
        self._purgar(ahora)
        if clave in self._valores:
            self._valores.move_to_end(clave)
            self._vencimientos.move_to_end(clave)
        elif len(self._valores) >= self._capacidad:
            # Tras la purga todas siguen vivas: sale la menos reciente.
            expulsada, _ = self._valores.popitem(last=False)
            del self._vencimientos[expulsada]
        self._valores[clave] = valor
        self._vencimientos[clave] = vencimiento

    def _vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except (TypeError, OverflowError):
            if not isinstance(ahora, numbers.Number):
                raise
            # Sumas que el operador no resuelve aunque ambos sean números,
            # como reloj float con ttl entero enorme o reloj Decimal con ttl
            # float: se usa la suma exacta, comparable con ambos tipos.
            return Fraction(ahora) + Fraction(self._ttl)

    def _purgar(self, ahora):
        vencidas = []
        for clave, vencimiento in self._vencimientos.items():
            if not ahora >= vencimiento:
                break
            vencidas.append(clave)
        for clave in vencidas:
            del self._vencimientos[clave]
            del self._valores[clave]
