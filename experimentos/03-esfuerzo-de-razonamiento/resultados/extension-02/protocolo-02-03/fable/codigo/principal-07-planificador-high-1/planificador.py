"""Planificador de tareas con dependencias.

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
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    """Administra el estado de un grafo acíclico de tareas."""

    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia propia: cada tarea queda con un frozenset de prerrequisitos.
        prerrequisitos = {}
        for nombre, requeridos in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(requeridos, (str, bytes, bytearray)):
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                requeridos = list(requeridos)
            except TypeError:
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable de nombres"
                ) from None
            for requerido in requeridos:
                if not _nombre_valido(requerido):
                    raise ValueError(
                        f"nombre de dependencia inválido en {nombre!r}: {requerido!r}"
                    )
            prerrequisitos[nombre] = frozenset(requeridos)

        dependientes = {nombre: [] for nombre in prerrequisitos}
        for nombre, requeridos in prerrequisitos.items():
            for requerido in requeridos:
                if requerido not in prerrequisitos:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {requerido!r}"
                    )
                dependientes[requerido].append(nombre)

        # Detección de ciclos (Kahn, iterativo). Una auto dependencia es un ciclo.
        faltantes = {
            nombre: len(requeridos) for nombre, requeridos in prerrequisitos.items()
        }
        restantes = dict(faltantes)
        cola = [nombre for nombre, cantidad in restantes.items() if cantidad == 0]
        visitadas = 0
        while cola:
            actual = cola.pop()
            visitadas += 1
            for dependiente in dependientes[actual]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    cola.append(dependiente)
        if visitadas != len(prerrequisitos):
            raise ValueError("las dependencias contienen un ciclo")

        habilitadas = [nombre for nombre, cantidad in faltantes.items() if cantidad == 0]
        heapq.heapify(habilitadas)

        # Se asigna todo al final para que un error no deje estado a medias.
        self._capacidad = capacidad
        self._dependientes = dependientes
        self._faltantes = faltantes  # prerrequisitos que aún no están listos
        self._habilitadas = habilitadas  # heap de pendientes con todo listo
        self._estados = {nombre: PENDIENTE for nombre in sorted(prerrequisitos)}
        self._en_curso = 0
        self._sin_terminar = len(prerrequisitos)

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza, en orden lexicográfico, las tareas habilitadas que entren."""
        lanzadas = []
        while self._habilitadas and self._en_curso < self._capacidad:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista o fallida."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso (estado: {self._estados[nombre]})"
            )

        self._en_curso -= 1
        self._sin_terminar -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                if (
                    self._faltantes[dependiente] == 0
                    and self._estados[dependiente] == PENDIENTE
                ):
                    heapq.heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            # Bloqueo transitivo: sólo se avanza por las recién bloqueadas,
            # porque las ya bloqueadas tienen bloqueada su descendencia.
            pila = [nombre]
            while pila:
                actual = pila.pop()
                for dependiente in self._dependientes[actual]:
                    if self._estados[dependiente] == PENDIENTE:
                        self._estados[dependiente] = BLOQUEADO
                        self._sin_terminar -= 1
                        pila.append(dependiente)
        return None

    def terminado(self):
        """Indica si todas las tareas están listas, fallidas o bloqueadas."""
        return self._sin_terminar == 0
