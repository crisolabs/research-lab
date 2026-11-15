"""Caché LRU con vencimiento por TTL y reloj inyectado."""

from __future__ import annotations

import math
from collections import OrderedDict
from fractions import Fraction
from typing import Any, Callable, Hashable

__all__ = ["Cache"]

# Centinela interno: distingue «clave ausente» de un valor guardado que es None.
_AUSENTE = object()


class Cache:
    """Caché LRU de capacidad fija cuyas entradas vencen por TTL.

    Cada escritura fija el vencimiento de la entrada en `ahora + ttl`, y la
    entrada está vencida cuando `ahora >= vencimiento`. Las lecturas actualizan
    la recencia pero no renuevan el TTL. El instante actual sale únicamente de
    `reloj`, un callable sin argumentos que devuelve segundos no decrecientes.
    """

    def __init__(self, capacidad: int, ttl: float, reloj: Callable[[], float]) -> None:
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo (no booleano)")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or not 0 < ttl < math.inf:
            raise ValueError("ttl debe ser un int o float finito y positivo (no booleano)")
        self._capacidad = capacidad
        self._ttl = ttl
        self._reloj = reloj
        # Dos órdenes sobre las mismas claves: `_valores` va de la menos a la
        # más recientemente usada y `_vencimientos` de la primera a la última
        # en vencer. Así desalojar y purgar cuestan O(1) por entrada.
        self._valores = OrderedDict()
        self._vencimientos = OrderedDict()
        self._hits = 0
        self._misses = 0

    def poner(self, clave: Hashable, valor: Any) -> None:
        """Guarda o reemplaza `valor`, renueva su TTL y lo deja como el más reciente."""
        ahora = self._purgar()
        self._guardar(clave, valor, ahora)

    def obtener(self, clave: Hashable, defecto: Any = None) -> Any:
        """Devuelve el valor vivo de `clave` (hit) o `defecto` (miss)."""
        self._purgar()
        valor = self._leer(clave)
        return defecto if valor is _AUSENTE else valor

    def obtener_o_crear(self, clave: Hashable, fabrica: Callable[[], Any]) -> Any:
        """Devuelve el valor vivo de `clave` (hit) o guarda y devuelve `fabrica()` (miss)."""
        self._purgar()
        valor = self._leer(clave)
        if valor is _AUSENTE:
            valor = fabrica()
            # Recién ahora se vuelve a mirar el reloj y se hace lugar: el TTL
            # empieza cuando la fábrica termina (pudo avanzar el reloj) y, si
            # la fábrica lanza, no se llegó a eliminar ninguna entrada viva.
            ahora = self._purgar()
            self._guardar(clave, valor, ahora)
        return valor

    def borrar(self, clave: Hashable) -> bool:
        """Elimina `clave` y devuelve si estaba viva."""
        self._purgar()
        if clave not in self._valores:
            return False
        del self._valores[clave]
        del self._vencimientos[clave]
        return True

    def claves(self) -> list:
        """Devuelve una lista nueva con las claves vivas, de menos a más reciente."""
        self._purgar()
        return list(self._valores)

    def estadisticas(self) -> dict:
        """Devuelve una copia de los contadores de hits y misses."""
        return {"hits": self._hits, "misses": self._misses}

    def _purgar(self):
        """Elimina todas las entradas vencidas y devuelve el instante consultado."""
        ahora = self._reloj()
        valores, vencimientos = self._valores, self._vencimientos
        while vencimientos:
            clave, vencimiento = next(iter(vencimientos.items()))
            if not ahora >= vencimiento:
                break  # Las que siguen vencen todavía más tarde.
            del vencimientos[clave]
            del valores[clave]
        return ahora

    def _leer(self, clave):
        """Busca `clave` sumando un hit o un miss; el hit la vuelve la más reciente."""
        valor = self._valores.get(clave, _AUSENTE)
        if valor is _AUSENTE:
            self._misses += 1
        else:
            self._hits += 1
            self._valores.move_to_end(clave)
        return valor

    def _guardar(self, clave, valor, ahora):
        """Escribe la entrada como la más reciente; las vencidas ya deben estar purgadas."""
        vencimiento = self._vencimiento(ahora)  # Antes de tocar nada, por si falla.
        valores, vencimientos = self._valores, self._vencimientos
        if clave not in valores and len(valores) >= self._capacidad:
            menos_reciente, _ = valores.popitem(last=False)
            del vencimientos[menos_reciente]
        valores[clave] = valor
        valores.move_to_end(clave)
        vencimientos[clave] = vencimiento
        vencimientos.move_to_end(clave)
        # Con ttl fijo y reloj no decreciente, lo último que se escribe es lo
        # último en vencer. Si alguna vez no fuera así (un reloj que retrocede
        # contra su contrato, o redondeos al mezclar int y float gigantes), se
        # reordena para que la purga siga siendo exacta.
        desde_el_final = reversed(vencimientos.values())
        next(desde_el_final)
        anterior = next(desde_el_final, None)
        if anterior is not None and vencimiento < anterior:
            for otra in sorted(vencimientos, key=vencimientos.__getitem__):
                vencimientos.move_to_end(otra)

    def _vencimiento(self, ahora):
        """Calcula `ahora + ttl`."""
        try:
            return ahora + self._ttl
        except OverflowError:
            # Un int válido puede no entrar en un float (p. ej. ttl=10**400 con
            # un reloj float): se guarda la suma exacta en lugar de fallar.
            return Fraction(ahora) + Fraction(self._ttl)
