"""Caché LRU con vencimiento basada en un reloj inyectado."""

import math
from collections import OrderedDict


class Cache:
    """Caché LRU con TTL por entrada.

    Cada entrada guarda ``(valor, vencimiento)``. Una entrada está vencida
    cuando ``ahora >= vencimiento``. El orden del ``OrderedDict`` refleja la
    recencia: el primer elemento es el menos recientemente usado.
    """

    def __init__(self, capacidad, ttl, reloj):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número positivo finito")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser un número positivo finito")
        if ttl <= 0:
            raise ValueError("ttl debe ser un número positivo finito")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._datos = OrderedDict()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Auxiliares internos
    # ------------------------------------------------------------------
    def _vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except OverflowError:
            return math.inf

    def _purgar(self, ahora):
        vencidas = [c for c, (_, venc) in self._datos.items() if ahora >= venc]
        for clave in vencidas:
            del self._datos[clave]

    def _guardar(self, clave, valor, ahora):
        venc = self._vencimiento(ahora)
        if clave in self._datos:
            self._datos[clave] = (valor, venc)
            self._datos.move_to_end(clave)
            return
        while len(self._datos) >= self._capacidad:
            self._datos.popitem(last=False)
        self._datos[clave] = (valor, venc)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return None

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._datos:
            self._datos.move_to_end(clave)
            self._hits += 1
            return self._datos[clave][0]
        self._misses += 1
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def claves(self):
        ahora = self._reloj()
        self._purgar(ahora)
        return list(self._datos.keys())

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
