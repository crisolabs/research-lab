"""Caché LRU con vencimiento por TTL y reloj inyectado."""

import math
from collections import OrderedDict

__all__ = ["Cache"]


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


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen tras ``ttl`` segundos.

    Las entradas se guardan en dos órdenes:

    * ``_datos``: clave -> valor, ordenado de menos a más recientemente usado.
    * ``_vencimientos``: clave -> instante de vencimiento, ordenado por
      vencimiento ascendente. Como el TTL es constante y el reloj no decrece,
      cada nuevo vencimiento es mayor o igual que todos los existentes, así que
      basta con mover la clave al final para mantener el orden. Esto permite
      purgar las entradas vencidas recorriendo sólo las que efectivamente
      vencieron.
    """

    __slots__ = ("_capacidad", "_ttl", "_reloj", "_datos", "_vencimientos",
                 "_hits", "_misses")

    def __init__(self, capacidad, ttl, reloj):
        self._capacidad = _validar_capacidad(capacidad)
        self._ttl = _validar_ttl(ttl)
        self._reloj = reloj
        self._datos = OrderedDict()
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Auxiliares internos
    # ------------------------------------------------------------------
    def _purgar(self, ahora):
        """Elimina todas las entradas con ``ahora >= vencimiento``."""
        vencimientos = self._vencimientos
        datos = self._datos
        while vencimientos:
            clave, vencimiento = next(iter(vencimientos.items()))
            if ahora >= vencimiento:
                del vencimientos[clave]
                del datos[clave]
            else:
                break

    def _guardar(self, clave, valor, ahora):
        """Guarda ``valor`` (ya purgadas las vencidas) con vencimiento nuevo."""
        datos = self._datos
        vencimientos = self._vencimientos
        if clave in datos:
            datos[clave] = valor
            datos.move_to_end(clave)
        else:
            if len(datos) >= self._capacidad:
                # Tras la purga todas las entradas están vivas: se descarta
                # la menos recientemente usada.
                lru, _ = datos.popitem(last=False)
                del vencimientos[lru]
            datos[clave] = valor
        vencimientos[clave] = ahora + self._ttl
        vencimientos.move_to_end(clave)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        datos = self._datos
        if clave in datos:
            datos.move_to_end(clave)
            self._hits += 1
            return datos[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        datos = self._datos
        if clave in datos:
            datos.move_to_end(clave)
            self._hits += 1
            return datos[clave]
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
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
