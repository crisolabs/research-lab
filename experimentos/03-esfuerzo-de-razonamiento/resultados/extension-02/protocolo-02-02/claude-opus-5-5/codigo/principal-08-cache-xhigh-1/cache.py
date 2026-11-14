"""Caché LRU con vencimiento por TTL basada en un reloj inyectado."""

import heapq
import itertools
import math
from collections import OrderedDict

__all__ = ["Cache"]

_FALTA = object()


def _validar_capacidad(capacidad):
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise ValueError("capacidad debe ser un entero positivo")
    if capacidad <= 0:
        raise ValueError("capacidad debe ser un entero positivo")
    return capacidad


def _validar_ttl(ttl):
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        raise ValueError("ttl debe ser un número finito positivo")
    if isinstance(ttl, float) and not math.isfinite(ttl):
        raise ValueError("ttl debe ser un número finito positivo")
    if not ttl > 0:
        raise ValueError("ttl debe ser un número finito positivo")
    return ttl


class _Entrada:
    __slots__ = ("valor", "vencimiento", "secuencia")

    def __init__(self, valor, vencimiento, secuencia):
        self.valor = valor
        self.vencimiento = vencimiento
        self.secuencia = secuencia


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen tras ``ttl`` segundos."""

    def __init__(self, capacidad, ttl, reloj):
        self._capacidad = _validar_capacidad(capacidad)
        self._ttl = _validar_ttl(ttl)
        self._reloj = reloj
        # clave -> _Entrada, ordenado de menos a más recientemente usado.
        self._datos = OrderedDict()
        # Montículo de (vencimiento, secuencia, clave) con borrado perezoso.
        # La secuencia es única, por lo que nunca se comparan las claves.
        self._vencimientos = []
        self._contador = itertools.count()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ #
    # Utilidades internas
    # ------------------------------------------------------------------ #
    def _purgar(self, ahora):
        """Elimina todas las entradas con ``ahora >= vencimiento``."""
        monticulo = self._vencimientos
        datos = self._datos
        while monticulo and monticulo[0][0] <= ahora:
            _, secuencia, clave = heapq.heappop(monticulo)
            entrada = datos.get(clave)
            if entrada is not None and entrada.secuencia == secuencia:
                del datos[clave]

    def _compactar(self):
        """Reconstruye el montículo si acumuló demasiadas referencias obsoletas."""
        if len(self._vencimientos) > 2 * len(self._datos) + 32:
            self._vencimientos = [
                (e.vencimiento, e.secuencia, k) for k, e in self._datos.items()
            ]
            heapq.heapify(self._vencimientos)

    def _guardar(self, clave, valor, ahora):
        """Guarda ``valor`` como el más reciente; asume la caché ya purgada."""
        datos = self._datos
        vencimiento = ahora + self._ttl
        secuencia = next(self._contador)
        if clave in datos:
            entrada = datos[clave]
            entrada.valor = valor
            entrada.vencimiento = vencimiento
            entrada.secuencia = secuencia
            datos.move_to_end(clave)
        else:
            while len(datos) >= self._capacidad:
                datos.popitem(last=False)
            datos[clave] = _Entrada(valor, vencimiento, secuencia)
        heapq.heappush(self._vencimientos, (vencimiento, secuencia, clave))
        self._compactar()

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #
    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _FALTA)
        if entrada is _FALTA:
            self._misses += 1
            return defecto
        self._datos.move_to_end(clave)
        self._hits += 1
        return entrada.valor

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _FALTA)
        if entrada is not _FALTA:
            self._datos.move_to_end(clave)
            self._hits += 1
            return entrada.valor
        self._misses += 1
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina; el reloj pudo avanzar.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            self._compactar()
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
