"""Caché LRU con vencimiento (TTL) que mide el tiempo con un reloj inyectado."""

import heapq
import itertools
import math
from collections import OrderedDict, namedtuple
from fractions import Fraction

__all__ = ["Cache"]

_Entrada = namedtuple("_Entrada", "valor vencimiento secuencia")


class Cache:
    """Caché LRU de capacidad fija con vencimiento por entrada.

    Cada entrada vence ``ttl`` segundos después de su última escritura con
    ``poner`` (las lecturas no renuevan el plazo) y se considera vencida
    cuando ``ahora >= vencimiento``. El tiempo sale sólo de ``reloj()``.
    """

    def __init__(self, capacidad, ttl, reloj):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if (
            not isinstance(ttl, (int, float))
            or isinstance(ttl, bool)
            or (isinstance(ttl, float) and not math.isfinite(ttl))
            or ttl <= 0
        ):
            raise ValueError("ttl debe ser un int o float finito y positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> _Entrada, de menos a más recientemente usada.
        self._entradas = OrderedDict()
        # Montículo de (vencimiento, secuencia, clave). Cuando una entrada se
        # reemplaza, borra o desaloja, su elemento queda obsoleto: se detecta
        # porque la secuencia ya no coincide y se descarta al salir.
        self._vencimientos = []
        self._secuencias = itertools.count()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        """Guarda o reemplaza ``clave`` como la más reciente, con TTL nuevo."""
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        """Devuelve el valor vivo de ``clave`` (hit) o ``defecto`` (miss)."""
        self._purgar(self._reloj())
        entrada = self._entradas.get(clave)
        if entrada is None:
            self._misses += 1
            return defecto
        self._entradas.move_to_end(clave)
        self._hits += 1
        return entrada.valor

    def obtener_o_crear(self, clave, fabrica):
        """Devuelve el valor vivo de ``clave`` o guarda y devuelve ``fabrica()``."""
        self._purgar(self._reloj())
        entrada = self._entradas.get(clave)
        if entrada is not None:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return entrada.valor
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin tocar las entradas.
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina. Mientras trabajaba el reloj
        # pudo avanzar, así que se vuelve a purgar antes de hacer lugar: sólo
        # se desaloja una entrada si sigue viva.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        """Elimina ``clave`` si está viva; devuelve si existía."""
        self._purgar(self._reloj())
        if clave not in self._entradas:
            return False
        del self._entradas[clave]
        self._compactar_si_conviene()
        return True

    def claves(self):
        """Devuelve una lista nueva de claves vivas, de menos a más reciente."""
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        """Devuelve una copia de los contadores de hits y misses."""
        return {"hits": self._hits, "misses": self._misses}

    def _purgar(self, ahora):
        """Elimina todas las entradas con ``ahora >= vencimiento``."""
        vencimientos = self._vencimientos
        entradas = self._entradas
        while vencimientos and ahora >= vencimientos[0][0]:
            _, secuencia, clave = heapq.heappop(vencimientos)
            entrada = entradas.get(clave)
            if entrada is not None and entrada.secuencia == secuencia:
                del entradas[clave]

    def _guardar(self, clave, valor, ahora):
        """Guarda ``valor``; requiere haber purgado recién con ``ahora``."""
        vencimiento = self._sumar_ttl(ahora)
        secuencia = next(self._secuencias)
        entradas = self._entradas
        if clave in entradas:
            entradas.move_to_end(clave)
        elif len(entradas) >= self._capacidad:
            # Tras la purga todas son vivas: sale la menos recientemente usada.
            entradas.popitem(last=False)
        entradas[clave] = _Entrada(valor, vencimiento, secuencia)
        heapq.heappush(self._vencimientos, (vencimiento, secuencia, clave))
        self._compactar_si_conviene()

    def _sumar_ttl(self, ahora):
        """Devuelve ``ahora + ttl``, en forma exacta si no entra en un float."""
        try:
            return ahora + self._ttl
        except OverflowError:
            # Un entero enorme (p. ej. el ttl) sumado a un float.
            try:
                return Fraction(ahora) + Fraction(self._ttl)
            except (OverflowError, ValueError):
                return ahora  # infinito o NaN: un ttl finito no lo altera

    def _compactar_si_conviene(self):
        """Reconstruye el montículo si la mayoría de sus elementos es obsoleta."""
        if len(self._vencimientos) > 2 * len(self._entradas) + 32:
            self._vencimientos = [
                (entrada.vencimiento, entrada.secuencia, clave)
                for clave, entrada in self._entradas.items()
            ]
            heapq.heapify(self._vencimientos)
