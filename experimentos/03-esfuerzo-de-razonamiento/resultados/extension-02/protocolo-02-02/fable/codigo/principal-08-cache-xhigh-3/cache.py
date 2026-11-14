"""Caché LRU con vencimiento (TTL) y reloj inyectado. Ver TAREA.md."""

import heapq
import math
from collections import OrderedDict
from fractions import Fraction

_AUSENTE = object()


class Cache:
    """Caché de capacidad acotada con política LRU y vencimiento por TTL.

    Todo el manejo del tiempo usa exclusivamente el reloj inyectado.
    """

    def __init__(self, capacidad, ttl, reloj):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número (int o float) positivo y finito")
        # Sólo los float pueden ser no finitos; math.isfinite sobre un int
        # enorme lanzaría OverflowError.
        if (isinstance(ttl, float) and not math.isfinite(ttl)) or ttl <= 0:
            raise ValueError("ttl debe ser un número (int o float) positivo y finito")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento, secuencia), de menos a más reciente.
        self._datos = OrderedDict()
        # Montículo de (vencimiento, secuencia, clave) con borrado perezoso:
        # un ítem sólo es válido si su secuencia coincide con la de la entrada
        # actual de esa clave.
        self._vencimientos = []
        self._secuencia = 0
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ API

    def poner(self, clave, valor):
        self._guardar(clave, valor, self._reloj())

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _AUSENTE)
        if entrada is _AUSENTE:
            self._misses += 1
            return defecto
        self._datos.move_to_end(clave)
        self._hits += 1
        return entrada[0]

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        entrada = self._datos.get(clave, _AUSENTE)
        if entrada is not _AUSENTE:
            self._datos.move_to_end(clave)
            self._hits += 1
            return entrada[0]
        self._misses += 1
        # Si la fábrica lanza, la excepción se propaga sin haber tocado
        # ninguna entrada: el desalojo ocurre recién al guardar.
        valor = fabrica()
        # El reloj pudo avanzar mientras la fábrica trabajaba: se relee para
        # que el TTL empiece ahora y para purgar lo que venció entretanto
        # antes de decidir si hace falta desalojar una entrada viva.
        self._guardar(clave, valor, self._reloj())
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._datos)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}

    # ------------------------------------------------------------- internos

    def _vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except OverflowError:
            # Mezcla de float con un int que no entra en un float: se suma
            # de forma exacta.
            return Fraction(ahora) + Fraction(self._ttl)

    def _purgar(self, ahora):
        """Elimina toda entrada con vencimiento <= ahora (frontera inclusiva)."""
        pendientes = self._vencimientos
        datos = self._datos
        while pendientes and pendientes[0][0] <= ahora:
            _, secuencia, clave = heapq.heappop(pendientes)
            entrada = datos.get(clave)
            if entrada is not None and entrada[2] == secuencia:
                del datos[clave]

    def _guardar(self, clave, valor, ahora):
        self._purgar(ahora)
        vencimiento = self._vencimiento(ahora)
        datos = self._datos
        if clave in datos:
            datos.move_to_end(clave)
        else:
            # Tras la purga sólo quedan entradas vivas: la primera es la
            # menos recientemente usada.
            while len(datos) >= self._capacidad:
                datos.popitem(last=False)
        self._secuencia += 1
        datos[clave] = (valor, vencimiento, self._secuencia)
        heapq.heappush(self._vencimientos, (vencimiento, self._secuencia, clave))
        # Los ítems obsoletos (reemplazos, borrados, desalojos) se descartan
        # al llegar a la cima; si se acumulan demasiados, se reconstruye.
        if len(self._vencimientos) > 2 * len(datos) + 16:
            self._vencimientos = [
                (entrada[1], entrada[2], k) for k, entrada in datos.items()
            ]
            heapq.heapify(self._vencimientos)
