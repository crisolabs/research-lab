"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

import heapq
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _nombre_valido(nombre):
    """Devuelve el nombre como ``str`` exacto o lanza ``ValueError``."""
    if not isinstance(nombre, str):
        raise ValueError(f"nombre de tarea inválido: {nombre!r}")
    if type(nombre) is not str:
        # Copia a str puro: una subclase podría alterar hash o comparación.
        nombre = str.__str__(nombre)
    if not nombre:
        raise ValueError("el nombre de una tarea no puede ser vacío")
    return nombre


class Planificador:
    """Administra el estado de un grafo acíclico de tareas."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        capacidad = int.__int__(capacidad)
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia de la entrada, validando nombres y descartando repeticiones.
        grafo = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            nombre = _nombre_valido(nombre)
            if nombre in grafo:
                raise ValueError(f"nombre de tarea duplicado: {nombre!r}")
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable"
                ) from None
            grafo[nombre] = {_nombre_valido(previo) for previo in iterador}

        nombres = sorted(grafo)
        dependientes = {nombre: [] for nombre in nombres}
        for nombre in nombres:
            for previo in grafo[nombre]:
                if previo not in grafo:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {previo!r}"
                    )
                dependientes[previo].append(nombre)

        # Detección de ciclos (algoritmo de Kahn, sin recursión).
        faltan = {nombre: len(grafo[nombre]) for nombre in nombres}
        libres = [nombre for nombre in nombres if not faltan[nombre]]
        visitadas = 0
        while libres:
            actual = libres.pop()
            visitadas += 1
            for siguiente in dependientes[actual]:
                faltan[siguiente] -= 1
                if not faltan[siguiente]:
                    libres.append(siguiente)
        if visitadas != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._dependientes = {
            nombre: tuple(dependientes[nombre]) for nombre in nombres
        }
        self._estados = {nombre: PENDIENTE for nombre in nombres}
        # Prerrequisitos que todavía no están listos, por tarea.
        self._faltan = {nombre: len(grafo[nombre]) for nombre in nombres}
        # Montículo de tareas pendientes con todos sus prerrequisitos listos.
        # `nombres` está ordenado, así que la lista ya es un montículo válido.
        self._habilitadas = [nombre for nombre in nombres if not self._faltan[nombre]]
        self._en_curso = 0
        self._abiertas = len(nombres)  # pendientes o en curso

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza tareas habilitadas, en orden lexicográfico, hasta la capacidad."""
        lanzadas = []
        while self._habilitadas and self._en_curso < self._capacidad:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista o fallida."""
        if type(exito) is not bool:
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str):
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if type(nombre) is not str:
            nombre = str.__str__(nombre)
        estado = self._estados.get(nombre)
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso (está {estado})")

        self._en_curso -= 1
        self._abiertas -= 1
        if exito:
            self._estados[nombre] = LISTO
            for siguiente in self._dependientes[nombre]:
                self._faltan[siguiente] -= 1
                if not self._faltan[siguiente] and self._estados[siguiente] == PENDIENTE:
                    heapq.heappush(self._habilitadas, siguiente)
            return None

        self._estados[nombre] = FALLO
        # Todo descendiente de un fallo sigue pendiente (nunca pudo lanzarse)
        # o ya fue bloqueado junto con sus propios descendientes.
        por_bloquear = [nombre]
        while por_bloquear:
            actual = por_bloquear.pop()
            for siguiente in self._dependientes[actual]:
                if self._estados[siguiente] == PENDIENTE:
                    self._estados[siguiente] = BLOQUEADO
                    self._abiertas -= 1
                    por_bloquear.append(siguiente)
        return None

    def terminado(self):
        """Indica si todas las tareas están en un estado final."""
        return self._abiertas == 0
