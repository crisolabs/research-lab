"""Implementá la caché pedida en TAREA.md."""

import heapq
import itertools
import math
from collections import OrderedDict


def _es_capacidad_valida(capacidad):
    return (
        isinstance(capacidad, int)
        and not isinstance(capacidad, bool)
        and capacidad > 0
    )


def _es_ttl_valido(ttl):
    if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
        return False
    try:
        return math.isfinite(ttl) and ttl > 0
    except OverflowError:  # entero demasiado grande para float
        return False


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if not _es_capacidad_valida(capacidad):
            raise ValueError("capacidad debe ser un entero positivo")
        if not _es_ttl_valido(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento, token), de menos a más reciente
        self._entradas = OrderedDict()
        # Montículo (vencimiento, token, clave) para purgar sin recorrer
        # todo. Puede tener entradas obsoletas (renovadas o eliminadas),
        # que se descartan al llegar a la cima.
        self._vencimientos = []
        self._tokens = itertools.count()
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        self._poner(clave, valor)
        return None

    def obtener(self, clave, defecto=None):
        self._purgar(self._reloj())
        if clave in self._entradas:
            return self._acierto(clave)
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar(self._reloj())
        if clave in self._entradas:
            return self._acierto(clave)
        self._misses += 1
        # Si la fábrica lanza, la excepción sale sin tocar el caché.
        valor = fabrica()
        # El TTL empieza cuando termina la fábrica.
        self._poner(clave, valor)
        return valor

    def borrar(self, clave):
        self._purgar(self._reloj())
        if clave in self._entradas:
            del self._entradas[clave]
            return True
        return False

    def claves(self):
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}

    def _acierto(self, clave):
        self._entradas.move_to_end(clave)
        self._hits += 1
        return self._entradas[clave][0]

    def _purgar(self, ahora):
        vencimientos = self._vencimientos
        while vencimientos and ahora >= vencimientos[0][0]:
            _, token, clave = heapq.heappop(vencimientos)
            entrada = self._entradas.get(clave)
            if entrada is not None and entrada[2] == token:
                del self._entradas[clave]

    def _poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        vencimiento = ahora + self._ttl
        if vencimiento <= ahora:
            # ttl ínfimo frente al reloj: la entrada nace ya vencida.
            self._entradas.pop(clave, None)
            return
        entradas = self._entradas
        if clave in entradas:
            entradas.move_to_end(clave)
        elif len(entradas) >= self._capacidad:
            entradas.popitem(last=False)  # la viva menos recientemente usada
        token = next(self._tokens)
        entradas[clave] = (valor, vencimiento, token)
        heapq.heappush(self._vencimientos, (vencimiento, token, clave))
        # Acota la memoria de las entradas obsoletas del montículo.
        if len(self._vencimientos) > 2 * len(entradas) + 16:
            self._reconstruir_vencimientos()

    def _reconstruir_vencimientos(self):
        self._vencimientos = [
            (vencimiento, token, clave)
            for clave, (_, vencimiento, token) in self._entradas.items()
        ]
        heapq.heapify(self._vencimientos)
