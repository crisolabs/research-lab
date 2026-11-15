"""Caché LRU con vencimiento por TTL, gobernada por un reloj inyectado."""

import heapq
import math
from collections import OrderedDict
from fractions import Fraction

__all__ = ["Cache"]

# Tuplas obsoletas que se toleran en el montículo antes de reconstruirlo.
_HOLGURA = 16


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen por TTL.

    El tiempo sale únicamente de `reloj`, un callable sin argumentos que
    devuelve segundos. Una entrada vence cuando `ahora >= vencimiento`.
    Escribirla renueva su TTL; leerla sólo actualiza su recencia.
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
            # Un int siempre es finito (y uno enorme desbordaría isfinite).
            or (isinstance(ttl, float) and not math.isfinite(ttl))
            or ttl <= 0
        ):
            raise ValueError("ttl debe ser un int o float finito y positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> (valor, vencimiento, serie), de menos a más reciente.
        self._entradas = OrderedDict()
        # Montículo de (vencimiento, serie, clave) con borrado perezoso: una
        # tupla sólo vale si su serie es la de la entrada actual de la clave.
        self._vencimientos = []
        self._serie = 0
        self._hits = 0
        self._misses = 0

    def poner(self, clave, valor):
        """Guarda o reemplaza `valor` con TTL nuevo, como el más reciente."""
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        """Devuelve el valor de `clave` (hit) o `defecto` si no está (miss)."""
        self._purgar(self._reloj())
        entrada = self._buscar(clave)
        return defecto if entrada is None else entrada[0]

    def obtener_o_crear(self, clave, fabrica):
        """Devuelve el valor de `clave`; si no está, lo crea con `fabrica()`.

        Si la fábrica lanza, la excepción se propaga sin tocar las entradas.
        """
        self._purgar(self._reloj())
        entrada = self._buscar(clave)
        if entrada is not None:
            return entrada[0]
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina. El reloj pudo avanzar
        # mientras tanto: se purga otra vez antes de hacer lugar, para no
        # desalojar una entrada viva habiendo vencidas.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        """Elimina `clave`; devuelve si existía una entrada viva."""
        self._purgar(self._reloj())
        return self._entradas.pop(clave, None) is not None

    def claves(self):
        """Devuelve una lista nueva con las claves vivas, de menos a más
        reciente."""
        self._purgar(self._reloj())
        return list(self._entradas)

    def estadisticas(self):
        """Devuelve una copia de los contadores de hits y misses."""
        return {"hits": self._hits, "misses": self._misses}

    def _purgar(self, ahora):
        """Elimina toda entrada con `ahora >= vencimiento`."""
        entradas = self._entradas
        monton = self._vencimientos
        while monton and ahora >= monton[0][0]:
            _, serie, clave = heapq.heappop(monton)
            entrada = entradas.get(clave)
            if entrada is not None and entrada[2] == serie:
                del entradas[clave]

    def _buscar(self, clave):
        """Cuenta el acceso y devuelve la entrada de `clave`, o None.

        Si la encuentra (hit) la deja como la más reciente; si no, es un miss.
        """
        entrada = self._entradas.get(clave)
        if entrada is None:
            self._misses += 1
        else:
            self._hits += 1
            self._entradas.move_to_end(clave)
        return entrada

    def _guardar(self, clave, valor, ahora):
        """Escribe la entrada con vencimiento `ahora + ttl`.

        Supone que las vencidas ya se purgaron: si hay que hacer lugar, la
        primera en orden de recencia es la entrada viva menos usada.
        """
        entradas = self._entradas
        vencimiento = self._calcular_vencimiento(ahora)
        es_nueva = clave not in entradas
        self._serie += 1
        heapq.heappush(self._vencimientos, (vencimiento, self._serie, clave))
        if es_nueva and len(entradas) >= self._capacidad:
            entradas.popitem(last=False)
        entradas[clave] = (valor, vencimiento, self._serie)
        entradas.move_to_end(clave)
        if len(self._vencimientos) > 2 * len(entradas) + _HOLGURA:
            self._compactar()

    def _calcular_vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except OverflowError:
            # Un entero que no entra en un float (p. ej. ttl=10**400 con un
            # reloj float): la suma se hace de forma exacta.
            return Fraction(ahora) + Fraction(self._ttl)

    def _compactar(self):
        """Reconstruye el montículo sólo con las entradas presentes."""
        self._vencimientos = [
            (vencimiento, serie, clave)
            for clave, (_, vencimiento, serie) in self._entradas.items()
        ]
        heapq.heapify(self._vencimientos)
