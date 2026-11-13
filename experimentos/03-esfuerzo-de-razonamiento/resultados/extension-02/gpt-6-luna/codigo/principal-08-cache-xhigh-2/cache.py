import math
from collections import OrderedDict


class Cache:
    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número finito positivo")
        if isinstance(ttl, float):
            ttl_valido = math.isfinite(ttl) and ttl > 0
        else:
            ttl_valido = ttl > 0
        if not ttl_valido:
            raise ValueError("ttl debe ser un número finito positivo")

        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        self._entradas = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar_vencidas(self, ahora):
        vencidas = [
            clave
            for clave, (_, vencimiento) in self._entradas.items()
            if ahora >= vencimiento
        ]
        for clave in vencidas:
            del self._entradas[clave]

    def _guardar(self, clave, valor, ahora):
        self._entradas[clave] = (valor, ahora + self._ttl)
        self._entradas.move_to_end(clave)
        if len(self._entradas) > self._capacidad:
            self._entradas.popitem(last=False)

    def poner(self, clave, valor):
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        if clave not in self._entradas:
            self._misses += 1
            return defecto

        valor, _ = self._entradas[clave]
        self._entradas.move_to_end(clave)
        self._hits += 1
        return valor

    def obtener_o_crear(self, clave, fabrica):
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        if clave in self._entradas:
            valor, _ = self._entradas[clave]
            self._entradas.move_to_end(clave)
            self._hits += 1
            return valor

        self._misses += 1
        valor = fabrica()
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        if clave not in self._entradas:
            return False
        del self._entradas[clave]
        return True

    def claves(self):
        ahora = self._reloj()
        self._purgar_vencidas(ahora)
        return list(self._entradas)

    def estadisticas(self):
        return {"hits": self._hits, "misses": self._misses}
