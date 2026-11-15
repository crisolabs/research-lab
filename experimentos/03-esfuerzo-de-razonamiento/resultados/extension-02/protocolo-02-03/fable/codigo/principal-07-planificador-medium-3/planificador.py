"""Planificador de dependencias: sólo administra estados de tareas."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        deps = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prerrequisitos, (str, bytes, bytearray)):
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                elementos = list(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from None
            for pre in elementos:
                if not _nombre_valido(pre):
                    raise ValueError(f"nombre de prerrequisito inválido: {pre!r}")
            deps[nombre] = frozenset(elementos)

        for nombre, pres in deps.items():
            for pre in pres:
                if pre not in deps:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {pre!r}"
                    )

        # Detección de ciclos (Kahn), iterativa.
        dependientes = {nombre: set() for nombre in deps}
        faltantes = {}
        for nombre, pres in deps.items():
            faltantes[nombre] = len(pres)
            for pre in pres:
                dependientes[pre].add(nombre)
        libres = [n for n, c in faltantes.items() if c == 0]
        vistos = 0
        while libres:
            actual = libres.pop()
            vistos += 1
            for dep in dependientes[actual]:
                faltantes[dep] -= 1
                if faltantes[dep] == 0:
                    libres.append(dep)
        if vistos != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

        self._deps = deps
        self._dependientes = {n: frozenset(d) for n, d in dependientes.items()}
        self._capacidad = capacidad
        self._estados = {nombre: PENDIENTE for nombre in deps}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        estados = self._estados
        libres = self._capacidad - sum(1 for e in estados.values() if e == EN_CURSO)
        if libres <= 0:
            return []
        habilitadas = sorted(
            nombre
            for nombre, estado in estados.items()
            if estado == PENDIENTE
            and all(estados[pre] == LISTO for pre in self._deps[nombre])
        )
        lanzadas = habilitadas[:libres]
        for nombre in lanzadas:
            estados[nombre] = EN_CURSO
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
        visitados = {nombre}
        while pila:
            actual = pila.pop()
            for dep in self._dependientes[actual]:
                if dep in visitados:
                    continue
                visitados.add(dep)
                if self._estados[dep] == PENDIENTE:
                    self._estados[dep] = BLOQUEADO
                pila.append(dep)
        return None

    def terminado(self):
        return all(estado in _FINALES for estado in self._estados.values())
