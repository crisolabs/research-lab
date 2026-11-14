"""Caché LRU con vencimiento por TTL basado en un reloj inyectado."""

import heapq
import math
from collections import OrderedDict

__all__ = ["Cache"]


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen tras ``ttl`` segundos.

    - Una entrada vence cuando ``ahora >= vencimiento``.
    - ``poner`` renueva el TTL; las lecturas sólo actualizan la recencia.
    - Toda operación (salvo ``estadisticas``) purga antes las entradas vencidas.
    """

    # Margen mínimo antes de compactar el montículo de vencimientos.
    _MARGEN_COMPACTACION = 32

    def __init__(self, capacidad, ttl, reloj):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(ttl, (int, float)) or isinstance(ttl, bool):
            raise ValueError("ttl debe ser un número int/float")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser finito")
        if not ttl > 0:
            raise ValueError("ttl debe ser positivo")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento, secuencia); orden = recencia (LRU primero).
        self._datos = OrderedDict()
        # Montículo de (vencimiento, secuencia, clave) con borrado perezoso.
        self._vencimientos = []
        self._secuencia = 0
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _purgar(self, ahora):
        """Elimina todas las entradas cuyo vencimiento es <= ``ahora``."""
        monticulo = self._vencimientos
        datos = self._datos
        while monticulo and monticulo[0][0] <= ahora:
            _, secuencia, clave = heapq.heappop(monticulo)
            entrada = datos.get(clave)
            if entrada is not None and entrada[2] == secuencia:
                del datos[clave]

    def _compactar_si_hace_falta(self):
        """Reconstruye el montículo si acumula demasiadas referencias obsoletas."""
        if len(self._vencimientos) > 2 * len(self._datos) + self._MARGEN_COMPACTACION:
            self._vencimientos = [
                (vencimiento, secuencia, clave)
                for clave, (_, vencimiento, secuencia) in self._datos.items()
            ]
            heapq.heapify(self._vencimientos)

    def _guardar(self, clave, valor, ahora):
        """Guarda ``valor`` (con las vencidas ya purgadas a ``ahora``)."""
        datos = self._datos
        if clave in datos:
            datos.move_to_end(clave)
        else:
            while len(datos) >= self._capacidad:
                datos.popitem(last=False)
        vencimiento = ahora + self._ttl
        self._secuencia += 1
        secuencia = self._secuencia
        datos[clave] = (valor, vencimiento, secuencia)
        heapq.heappush(self._vencimientos, (vencimiento, secuencia, clave))
        self._compactar_si_hace_falta()

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
            return datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        datos = self._datos
        if clave in datos:
            datos.move_to_end(clave)
            self._hits += 1
            return datos[clave][0]
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
            self._compactar_si_hace_falta()
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
