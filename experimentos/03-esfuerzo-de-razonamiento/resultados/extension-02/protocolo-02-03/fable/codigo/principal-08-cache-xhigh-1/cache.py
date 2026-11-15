"""Caché LRU con vencimiento por TTL y reloj inyectado."""

import heapq
import math
from collections import OrderedDict

_AUSENTE = object()


class Cache:
    """Caché de capacidad fija con política LRU y vencimiento por TTL.

    El tiempo se obtiene únicamente del ``reloj`` inyectado. Una entrada vence
    cuando ``ahora >= vencimiento``.
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
        # clave -> (valor, serie, vencimiento), de menos a más reciente.
        self._entradas = OrderedDict()
        # Montículo de (vencimiento, serie, clave). Una tupla sólo es válida si
        # su serie coincide con la de la entrada actual de esa clave; las demás
        # son restos de reemplazos o borrados y se descartan al encontrarlas.
        self._vencimientos = []
        self._serie = 0
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ API

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        entrada = self._entradas.get(clave, _AUSENTE)
        if entrada is _AUSENTE:
            self._misses += 1
            return defecto
        self._entradas.move_to_end(clave)
        self._hits += 1
        return entrada[0]

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        entrada = self._entradas.get(clave, _AUSENTE)
        if entrada is not _AUSENTE:
            self._entradas.move_to_end(clave)
            self._hits += 1
            return entrada[0]

        self._misses += 1
        # Nada se desaloja antes de saber que la fábrica terminó bien.
        valor = fabrica()
        # El reloj pudo avanzar: el TTL arranca ahora y lo que haya vencido
        # mientras tanto se purga antes de decidir si hay que desalojar.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave not in self._entradas:
            return False
        del self._entradas[clave]
        self._compactar()
        return True

    def claves(self):
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}

    # ------------------------------------------------------------- internos

    def _purgar(self, ahora):
        """Elimina todas las entradas con ``ahora >= vencimiento``."""
        entradas = self._entradas
        pendientes = self._vencimientos
        while pendientes and ahora >= pendientes[0][0]:
            _, serie, clave = heapq.heappop(pendientes)
            entrada = entradas.get(clave, _AUSENTE)
            if entrada is not _AUSENTE and entrada[1] == serie:
                del entradas[clave]

    def _guardar(self, clave, valor, ahora):
        """Guarda o reemplaza ``clave`` como la más reciente (ya purgado)."""
        entradas = self._entradas
        try:
            vencimiento = ahora + self._ttl
        except OverflowError:
            # ttl entero demasiado grande para sumarlo a un reloj flotante.
            vencimiento = math.inf

        if clave not in entradas and len(entradas) >= self._capacidad:
            entradas.popitem(last=False)

        self._serie += 1
        entradas[clave] = (valor, self._serie, vencimiento)
        entradas.move_to_end(clave)
        heapq.heappush(self._vencimientos, (vencimiento, self._serie, clave))
        self._compactar()

    def _compactar(self):
        """Reconstruye el montículo si acumuló demasiadas tuplas obsoletas."""
        entradas = self._entradas
        if len(self._vencimientos) <= 2 * len(entradas) + 16:
            return
        self._vencimientos = [
            (vencimiento, serie, clave)
            for clave, (_, serie, vencimiento) in entradas.items()
        ]
        heapq.heapify(self._vencimientos)
