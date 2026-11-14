"""Planificador de dependencias: sólo administra estados de tareas."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = (LISTO, FALLO, BLOQUEADO)


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        deps = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            try:
                elementos = list(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable"
                ) from None
            for previo in elementos:
                if not _nombre_valido(previo):
                    raise ValueError(f"nombre de dependencia inválido: {previo!r}")
            deps[str(nombre)] = frozenset(str(p) for p in elementos)

        for nombre, previos in deps.items():
            for previo in previos:
                if previo not in deps:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {previo!r}"
                    )

        dependientes = {nombre: set() for nombre in deps}
        for nombre, previos in deps.items():
            for previo in previos:
                dependientes[previo].add(nombre)

        # Detección de ciclos (algoritmo de Kahn, sin recursión).
        faltantes = {nombre: len(previos) for nombre, previos in deps.items()}
        libres = [nombre for nombre, n in faltantes.items() if n == 0]
        procesadas = 0
        while libres:
            actual = libres.pop()
            procesadas += 1
            for siguiente in dependientes[actual]:
                faltantes[siguiente] -= 1
                if faltantes[siguiente] == 0:
                    libres.append(siguiente)
        if procesadas != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._deps = deps
        self._dependientes = dependientes
        self._estados = {nombre: PENDIENTE for nombre in deps}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        lugares = self._capacidad - en_curso
        if lugares <= 0:
            return []
        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == PENDIENTE
            and all(self._estados[p] == LISTO for p in self._deps[nombre])
        )
        lanzadas = habilitadas[:lugares]
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        vistos = {nombre}
        while pila:
            actual = pila.pop()
            for siguiente in self._dependientes[actual]:
                if siguiente in vistos:
                    continue
                vistos.add(siguiente)
                if self._estados[siguiente] == PENDIENTE:
                    self._estados[siguiente] = BLOQUEADO
                pila.append(siguiente)
        return None

    def terminado(self):
        return all(e in _FINALES for e in self._estados.values())
