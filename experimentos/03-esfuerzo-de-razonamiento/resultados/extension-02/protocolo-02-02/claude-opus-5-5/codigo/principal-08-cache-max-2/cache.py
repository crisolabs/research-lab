"""Caché LRU con vencimiento por TTL que usa sólo un reloj inyectado."""

import math
from collections import OrderedDict

__all__ = ["Cache"]

# Marca interna para distinguir "la clave no está" de un valor guardado None.
_FALTA = object()


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen ``ttl`` segundos
    después de escribirse.

    Invariante: como el TTL es el mismo para todas las entradas y el reloj no
    decrece, el orden de escritura coincide con el orden de vencimiento. Por
    eso ``_vencimientos`` siempre está ordenado y las entradas vencidas se
    purgan desde su frente en tiempo amortizado constante.
    """

    def __init__(self, capacidad, ttl, reloj):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo (no booleano)")
        if (
            isinstance(ttl, bool)
            or not isinstance(ttl, (int, float))
            or (isinstance(ttl, float) and not math.isfinite(ttl))
            or not ttl > 0
        ):
            raise ValueError(
                "ttl debe ser un int o float finito y positivo (no booleano)"
            )
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # clave -> valor, de menos a más recientemente usada.
        self._valores = OrderedDict()
        # clave -> vencimiento, de menor a mayor vencimiento.
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    # -- API pública -------------------------------------------------------

    def poner(self, clave, valor):
        """Guarda o reemplaza ``clave`` con vencimiento ``ahora + ttl``."""
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)

    def obtener(self, clave, defecto=None):
        """Devuelve el valor vivo de ``clave`` (hit) o ``defecto`` (miss)."""
        valor = self._leer(clave)
        return defecto if valor is _FALTA else valor

    def obtener_o_crear(self, clave, fabrica):
        """Devuelve el valor vivo de ``clave`` o lo crea con ``fabrica()``."""
        valor = self._leer(clave)
        if valor is not _FALTA:
            return valor
        # Si la fábrica lanza, la excepción se propaga sin tocar el caché.
        valor = fabrica()
        # El TTL empieza cuando la fábrica termina. Mientras trabajaba el reloj
        # pudo avanzar y vencer otras entradas: se purgan antes de decidir si
        # hace falta desalojar alguna viva.
        ahora = self._reloj()
        self._purgar(ahora)
        self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave):
        """Elimina ``clave`` si está viva; devuelve si existía."""
        self._purgar(self._reloj())
        if clave in self._valores:
            del self._valores[clave]
            del self._vencimientos[clave]
            return True
        return False

    def claves(self):
        """Lista nueva con las claves vivas, de menos a más reciente."""
        self._purgar(self._reloj())
        return list(self._valores)

    def estadisticas(self):
        """Copia de los contadores; no consulta el reloj ni altera el estado."""
        return {"hits": self._hits, "misses": self._misses}

    # -- Auxiliares --------------------------------------------------------

    def _purgar(self, ahora):
        """Elimina todas las entradas vencidas (``ahora >= vencimiento``)."""
        vencimientos = self._vencimientos
        while vencimientos:
            clave, vencimiento = next(iter(vencimientos.items()))
            if not ahora >= vencimiento:
                break  # Las demás vencen todavía más tarde.
            del vencimientos[clave]
            del self._valores[clave]

    def _leer(self, clave):
        """Purga y busca ``clave``. Si está viva la marca como la más reciente
        (sin renovar su TTL) y suma un hit; si no, suma un miss. Devuelve el
        valor o ``_FALTA``."""
        self._purgar(self._reloj())
        valores = self._valores
        if clave in valores:
            valores.move_to_end(clave)
            self._hits += 1
            return valores[clave]
        self._misses += 1
        return _FALTA

    def _guardar(self, clave, valor, ahora):
        """Guarda ``clave`` como la más reciente con vencimiento ``ahora + ttl``
        y, si es nueva y no hay lugar, desaloja la menos reciente. Supone que
        ya se purgaron las vencidas, así que la desalojada está viva."""
        try:
            vencimiento = ahora + self._ttl
        except OverflowError:
            # Un int enorme no se puede sumar a un float: el vencimiento real
            # está más allá de cualquier float finito.
            vencimiento = math.inf
        valores = self._valores
        vencimientos = self._vencimientos
        if clave in valores:
            valores.move_to_end(clave)
            vencimientos.move_to_end(clave)
        elif len(valores) >= self._capacidad:
            menos_reciente, _ = valores.popitem(last=False)
            del vencimientos[menos_reciente]
        valores[clave] = valor
        vencimientos[clave] = vencimiento
