import math
from collections import OrderedDict
from fractions import Fraction


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if (
            isinstance(ttl, bool)
            or not isinstance(ttl, (int, float))
            or ttl <= 0
            or (isinstance(ttl, float) and not math.isfinite(ttl))
        ):
            raise ValueError("ttl debe ser un número finito positivo")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self, ahora):
        vencidas = [
            clave
            for clave, (_, vencimiento) in self._entradas.items()
            if ahora >= vencimiento
        ]
        for clave in vencidas:
            del self._entradas[clave]

    def _vencimiento(self, ahora):
        try:
            return ahora + self._ttl
        except OverflowError:
            if isinstance(ahora, float) and not math.isfinite(ahora):
                return ahora
            if isinstance(ahora, (int, float)) and isinstance(self._ttl, (int, float)):
                return Fraction(ahora) + Fraction(self._ttl)
            raise

    def _guardar(self, clave, valor, vencimiento):
        if clave in self._entradas:
            self._entradas[clave] = (valor, vencimiento)
            self._entradas.move_to_end(clave)
            return

        if len(self._entradas) >= self._capacidad:
            self._entradas.popitem(last=False)
        self._entradas[clave] = (valor, vencimiento)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, self._vencimiento(ahora))

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave not in self._entradas:
            self._misses += 1
            return defecto

        valor = self._entradas[clave][0]
        self._entradas.move_to_end(clave)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave in self._entradas:
            valor = self._entradas[clave][0]
            self._entradas.move_to_end(clave)
            self._hits += 1
            return valor

        self._misses += 1
        valor = fabrica()
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, self._vencimiento(ahora))
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar(ahora)
        if clave not in self._entradas:
            return False
        del self._entradas[clave]
        return True

    def claves(self):
        ahora = self._reloj()
        self._purgar(ahora)
        return list(self._entradas.keys())

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
