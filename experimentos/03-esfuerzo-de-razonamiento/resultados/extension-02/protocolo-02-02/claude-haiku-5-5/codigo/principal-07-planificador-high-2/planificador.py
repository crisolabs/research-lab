"""Planificador de tareas con dependencias (ver TAREA.md).

Sólo administra estados: no crea threads ni ejecuta callbacks.
"""

from collections.abc import Mapping

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({_LISTO, _FALLO, _BLOQUEADO})


def _validar_nombre(nombre):
    """Devuelve el nombre si es un string no vacío; si no, lanza ValueError."""
    if not isinstance(nombre, str) or nombre == "":
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra el estado de un grafo de tareas con dependencias."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser positiva")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia propia: sets inmutables, sin referencias a la entrada.
        deps = {}
        for nombre, prerrequisitos in dependencias.items():
            _validar_nombre(nombre)
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"prerrequisitos de {nombre!r} no son iterables"
                ) from None
            conjunto = set()
            for prereq in iterador:
                conjunto.add(_validar_nombre(prereq))
            deps[nombre] = conjunto

        # Referencias a tareas inexistentes.
        for nombre, conjunto in deps.items():
            for prereq in conjunto:
                if prereq not in deps:
                    raise ValueError(
                        f"{nombre!r} depende de tarea desconocida {prereq!r}"
                    )

        # Detección de ciclos (incluye auto dependencias) por Kahn.
        grado = {n: len(c) for n, c in deps.items()}
        inversas = {n: [] for n in deps}
        for nombre, conjunto in deps.items():
            for prereq in conjunto:
                inversas[prereq].append(nombre)
        cola = [n for n, g in grado.items() if g == 0]
        procesadas = 0
        while cola:
            actual = cola.pop()
            procesadas += 1
            for dependiente in inversas[actual]:
                grado[dependiente] -= 1
                if grado[dependiente] == 0:
                    cola.append(dependiente)
        if procesadas != len(deps):
            raise ValueError("el grafo contiene ciclos de dependencias")

        self._capacidad = capacidad
        self._deps = {n: frozenset(c) for n, c in deps.items()}
        self._dependientes = {n: frozenset(v) for n, v in inversas.items()}
        self._estados = {n: _PENDIENTE for n in deps}

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza las tareas habilitadas que quepan en la capacidad libre.

        Devuelve la lista de nombres lanzados, en orden lexicográfico.
        """
        en_curso = sum(1 for e in self._estados.values() if e == _EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != _PENDIENTE:
                continue
            if all(self._estados[p] == _LISTO for p in self._deps[nombre]):
                self._estados[nombre] = _EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea en curso.

        Con éxito pasa a `listo`; si no, a `fallo` y bloquea en cascada
        las tareas pendientes que dependen de ella. Ante error no cambia nada.
        """
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != _EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en_curso "
                f"(estado: {self._estados[nombre]})"
            )

        if exito:
            self._estados[nombre] = _LISTO
            return None

        self._estados[nombre] = _FALLO
        pila = [nombre]
        while pila:
            actual = pila.pop()
            for dependiente in self._dependientes[actual]:
                if self._estados[dependiente] == _PENDIENTE:
                    self._estados[dependiente] = _BLOQUEADO
                    pila.append(dependiente)
        return None

    def terminado(self):
        """True si todas las tareas están listo, fallo o bloqueado."""
        return all(e in _TERMINALES for e in self._estados.values())
