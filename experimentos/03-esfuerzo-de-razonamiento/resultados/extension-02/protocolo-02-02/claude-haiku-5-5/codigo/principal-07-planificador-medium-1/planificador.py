"""Planificador de tareas con dependencias, según TAREA.md.

El módulo sólo administra estados: no crea hilos ni ejecuta callbacks.
"""

from collections import deque
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra el estado de tareas con dependencias y capacidad limitada."""

    def __init__(self, dependencias, capacidad):
        # Validación completa antes de tocar cualquier estado interno.
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        grafo = {}
        for nombre, prerrequisitos in dependencias.items():
            _validar_nombre(nombre)
            if isinstance(prerrequisitos, (str, bytes)) or not hasattr(prerrequisitos, "__iter__"):
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}")
            conjunto = set()
            for pre in prerrequisitos:
                _validar_nombre(pre)
                conjunto.add(pre)
            grafo[nombre] = frozenset(conjunto)

        for nombre, pres in grafo.items():
            for pre in pres:
                if pre not in grafo:
                    raise ValueError(f"referencia desconocida: {pre!r} (de {nombre!r})")
        for nombre, pres in grafo.items():
            if nombre in pres:
                raise ValueError(f"ciclo (auto dependencia): {nombre!r}")

        # Detección de ciclos con Kahn: si no se pueden ordenar todos, hay ciclo.
        grado = {n: len(p) for n, p in grafo.items()}
        dependientes = {n: set() for n in grafo}
        for nombre, pres in grafo.items():
            for pre in pres:
                dependientes[pre].add(nombre)
        cola = deque(n for n, g in grado.items() if g == 0)
        visitados = 0
        while cola:
            actual = cola.popleft()
            visitados += 1
            for dep in dependientes[actual]:
                grado[dep] -= 1
                if grado[dep] == 0:
                    cola.append(dep)
        if visitados != len(grafo):
            raise ValueError("el grafo contiene ciclos")

        self._prerrequisitos = grafo
        self._dependientes = {n: frozenset(d) for n, d in dependientes.items()}
        self._capacidad = capacidad
        self._estados = {n: PENDIENTE for n in grafo}

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza nuevas tareas habilitadas hasta llenar la capacidad libre."""
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        habilitadas = sorted(
            n
            for n, e in self._estados.items()
            if e == PENDIENTE
            and all(self._estados[p] == LISTO for p in self._prerrequisitos[n])
        )
        lanzadas = habilitadas[:libres]
        for n in lanzadas:
            self._estados[n] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista o fallida."""
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        visitados = {nombre}
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for dep in self._dependientes[actual]:
                if dep in visitados:
                    continue
                visitados.add(dep)
                if self._estados[dep] == PENDIENTE:
                    self._estados[dep] = BLOQUEADO
                cola.append(dep)
        return None

    def terminado(self):
        """True si todas las tareas están en un estado terminal."""
        return all(e in _TERMINALES for e in self._estados.values())
