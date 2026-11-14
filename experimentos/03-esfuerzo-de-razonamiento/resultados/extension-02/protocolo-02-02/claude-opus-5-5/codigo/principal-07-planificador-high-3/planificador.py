"""Planificador de dependencias: administra estados de tareas con capacidad limitada."""

from collections.abc import Mapping

__all__ = ["Planificador"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class _EntradaInvalida(TypeError, ValueError):
    """Error de entrada; es a la vez ValueError y TypeError."""


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _EntradaInvalida("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise _EntradaInvalida("dependencias debe ser un diccionario")

        try:
            items = list(dependencias.items())
        except Exception as exc:  # pragma: no cover - mapeos defectuosos
            raise ValueError("no se pudieron leer las dependencias") from exc

        deps = {}
        for nombre, prereqs in items:
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)):
                raise _EntradaInvalida(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                lista = list(prereqs)
            except TypeError as exc:
                raise _EntradaInvalida(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from exc
            conjunto = set()
            for prereq in lista:
                if not _nombre_valido(prereq):
                    raise ValueError(f"prerrequisito inválido en {nombre!r}: {prereq!r}")
                conjunto.add(prereq)
            deps[nombre] = frozenset(conjunto)

        for nombre, prereqs in deps.items():
            for prereq in prereqs:
                if prereq not in deps:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {prereq!r}"
                    )

        self._verificar_ciclos(deps)

        dependientes = {nombre: set() for nombre in deps}
        for nombre, prereqs in deps.items():
            for prereq in prereqs:
                dependientes[prereq].add(nombre)

        self._capacidad = capacidad
        self._deps = deps
        self._dependientes = {n: frozenset(s) for n, s in dependientes.items()}
        self._estados = {nombre: PENDIENTE for nombre in deps}

    @staticmethod
    def _verificar_ciclos(deps):
        # Algoritmo de Kahn: si no se pueden ordenar todas, hay un ciclo.
        faltantes = {nombre: len(prereqs) for nombre, prereqs in deps.items()}
        dependientes = {nombre: [] for nombre in deps}
        for nombre, prereqs in deps.items():
            for prereq in prereqs:
                dependientes[prereq].append(nombre)
        cola = [n for n, c in faltantes.items() if c == 0]
        procesadas = 0
        while cola:
            actual = cola.pop()
            procesadas += 1
            for dep in dependientes[actual]:
                faltantes[dep] -= 1
                if faltantes[dep] == 0:
                    cola.append(dep)
        if procesadas != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == PENDIENTE
            and all(self._estados[p] == LISTO for p in self._deps[nombre])
        )
        lanzadas = habilitadas[:libres]
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise _EntradaInvalida("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = list(self._dependientes[nombre])
        vistos = set()
        while pila:
            actual = pila.pop()
            if actual in vistos:
                continue
            vistos.add(actual)
            if self._estados[actual] == PENDIENTE:
                self._estados[actual] = BLOQUEADO
            pila.extend(self._dependientes[actual])
        return None

    def terminado(self):
        return all(
            estado in (LISTO, FALLO, BLOQUEADO) for estado in self._estados.values()
        )
