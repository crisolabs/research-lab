import math
from collections import OrderedDict


class Cache:
    """Caché LRU con vencimiento por TTL y reloj inyectado."""

    def __init__(self, capacidad, ttl, reloj):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl debe ser un número finito positivo")
        if isinstance(ttl, float) and not math.isfinite(ttl):
            raise ValueError("ttl debe ser un número finito positivo")
        if ttl <= 0:
            raise ValueError("ttl debe ser un número finito positivo")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, ordenado de menos a más recientemente usado.
        self._datos = OrderedDict()
        # clave -> vencimiento, ordenado por vencimiento creciente (el TTL es
        # constante y el reloj no decrece, así que el orden de escritura sirve).
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _purgar(self):
        ahora = self._reloj()
        venc = self._vencimientos
        while venc:
            clave = next(iter(venc))
            if ahora >= venc[clave]:
                del venc[clave]
                del self._datos[clave]
            else:
                break
        return ahora

    def _guardar(self, clave, valor, ahora):
        if clave not in self._datos and len(self._datos) >= self._capacidad:
            vieja, _ = self._datos.popitem(last=False)
            del self._vencimientos[vieja]
        self._datos[clave] = valor
        self._datos.move_to_end(clave)
        self._vencimientos[clave] = ahora + self._ttl
        self._vencimientos.move_to_end(clave)

    def poner(self, clave, valor):
        ahora = self._purgar()
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        self._purgar()
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave]
        self._misses += 1
        return defecto

    def obtener_o_crear(self, clave, fabrica):
        self._purgar()
        if clave in self._datos:
            self._hits += 1
            self._datos.move_to_end(clave)
            return self._datos[clave]
        self._misses += 1
        valor = fabrica()
        # El reloj pudo avanzar durante la fábrica: se vuelve a purgar para no
        # desalojar una entrada viva habiendo vencidas, y el TTL arranca ahora.
        ahora = self._purgar()
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        self._purgar()
        if clave in self._datos:
            del self._datos[clave]
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        self._purgar()
        return list(self._datos)

    def estadisticas(self):
        return {'hits': self._hits, 'misses': self._misses}
