"""Planificador de tareas con dependencias, según TAREA.md.

Sólo administra estados: no crea hilos ni ejecuta callbacks.
"""

from collections import deque
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_ESTADOS_TERMINALES = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra el estado de tareas con dependencias y capacidad limitada."""

    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise TypeError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise TypeError("capacidad debe ser un entero")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser positiva")

        # Validar y copiar todo antes de asignar nada (la excepción no deja estado parcial).
        prereq = {}
        for nombre, valores in dependencias.items():
            _validar_nombre(nombre)
            if isinstance(valores, (str, bytes)) or not hasattr(valores, "__iter__"):
                raise TypeError(f"prerrequisitos de {nombre!r} deben ser un iterable")
            conjunto = set()
            for pre in valores:
                _validar_nombre(pre)
                conjunto.add(pre)
            prereq[nombre] = frozenset(conjunto)

        for nombre, pres in prereq.items():
            for pre in pres:
                if pre not in prereq:
                    raise ValueError(f"referencia desconocida: {pre!r} (de {nombre!r})")

        _verificar_sin_ciclos(prereq)

        dependientes = {nombre: set() for nombre in prereq}
        for nombre, pres in prereq.items():
            for pre in pres:
                dependientes[pre].add(nombre)

        self._capacidad = capacidad
        self._prereq = prereq
        self._dependientes = dependientes
        self._estado = {nombre: PENDIENTE for nombre in prereq}

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estado)

    def tomar(self):
        """Lanza nuevas tareas habilitadas hasta llenar la capacidad libre."""
        en_curso = sum(1 for e in self._estado.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []

        lanzadas = []
        for nombre in sorted(self._estado):
            if len(lanzadas) >= libres:
                break
            if self._estado[nombre] != PENDIENTE:
                continue
            if all(self._estado[pre] == LISTO for pre in self._prereq[nombre]):
                self._estado[nombre] = EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como terminada con éxito o fallida."""
        if not isinstance(nombre, str) or nombre not in self._estado:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estado[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estado[nombre] = LISTO
            return None

        self._estado[nombre] = FALLO
        # Bloquear transitivamente todas las pendientes que dependan de esta tarea.
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for dep in self._dependientes[actual]:
                if self._estado[dep] == PENDIENTE:
                    self._estado[dep] = BLOQUEADO
                    cola.append(dep)
        return None

    def terminado(self):
        """True si todas las tareas están listo, fallo o bloqueado."""
        return all(e in _ESTADOS_TERMINALES for e in self._estado.values())


def _verificar_sin_ciclos(prereq):
    """Lanza ValueError si el grafo de prerrequisitos tiene ciclos (Kahn)."""
    grado = {nombre: len(pres) for nombre, pres in prereq.items()}
    dependientes = {nombre: [] for nombre in prereq}
    for nombre, pres in prereq.items():
        for pre in pres:
            dependientes[pre].append(nombre)

    cola = deque(n for n, g in grado.items() if g == 0)
    visitados = 0
    while cola:
        actual = cola.popleft()
        visitados += 1
        for dep in dependientes[actual]:
            grado[dep] -= 1
            if grado[dep] == 0:
                cola.append(dep)

    if visitados != len(prereq):
        raise ValueError("ciclo de dependencias detectado")
