"""Planificador de dependencias: administra estados de tareas sin ejecutarlas."""

from collections import deque
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or nombre == "":
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra el estado de un grafo de tareas con capacidad limitada.

    Todas las validaciones ocurren antes de modificar el estado interno, de
    modo que una excepción nunca deja el planificador a medio cambiar.
    """

    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")

        prereq = {}
        for nombre, prerrequisitos in dependencias.items():
            _validar_nombre(nombre)
            try:
                items = list(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"prerrequisitos no iterables para {nombre!r}"
                ) from None
            prereq[nombre] = frozenset(_validar_nombre(p) for p in items)

        for nombre, deps in prereq.items():
            for p in deps:
                if p not in prereq:
                    raise ValueError(
                        f"referencia desconocida: {p!r} en {nombre!r}"
                    )

        # Kahn: si no se pueden ordenar todos los nodos hay ciclo
        # (la auto dependencia queda incluida, porque nunca llega a grado 0).
        grado = {n: len(d) for n, d in prereq.items()}
        dependientes = {n: [] for n in prereq}
        for n, deps in prereq.items():
            for p in deps:
                dependientes[p].append(n)
        cola = deque(n for n, g in grado.items() if g == 0)
        procesados = 0
        while cola:
            actual = cola.popleft()
            procesados += 1
            for d in dependientes[actual]:
                grado[d] -= 1
                if grado[d] == 0:
                    cola.append(d)
        if procesados != len(prereq):
            raise ValueError("ciclo de dependencias")

        self._prereq = prereq
        self._dependientes = {
            n: frozenset(v) for n, v in dependientes.items()
        }
        self._estado = {n: PENDIENTE for n in sorted(prereq)}
        self._capacidad = capacidad

    def estados(self):
        return dict(self._estado)

    def tomar(self):
        ocupados = sum(1 for e in self._estado.values() if e == EN_CURSO)
        libres = self._capacidad - ocupados
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._estado):
            if len(lanzadas) >= libres:
                break
            if self._estado[nombre] != PENDIENTE:
                continue
            if all(self._estado[p] == LISTO for p in self._prereq[nombre]):
                self._estado[nombre] = EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estado:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estado[nombre] != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en_curso "
                f"(estado: {self._estado[nombre]})"
            )
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estado[nombre] = LISTO
            return None

        self._estado[nombre] = FALLO
        visitados = {nombre}
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for d in self._dependientes[actual]:
                if d in visitados:
                    continue
                visitados.add(d)
                cola.append(d)
                if self._estado[d] == PENDIENTE:
                    self._estado[d] = BLOQUEADO
        return None

    def terminado(self):
        return all(e in _TERMINALES for e in self._estado.values())
