"""Planificador de dependencias: administra estados de tareas con prerrequisitos."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        deps = {}
        for nombre, prereqs in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)):
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}")
            try:
                elementos = list(prereqs)
            except TypeError:
                raise ValueError(f"prerrequisitos no iterables para {nombre!r}") from None
            conjunto = set()
            for p in elementos:
                if not _nombre_valido(p):
                    raise ValueError(f"prerrequisito inválido en {nombre!r}: {p!r}")
                conjunto.add(p)
            deps[nombre] = frozenset(conjunto)

        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError(f"prerrequisito desconocido {p!r} en {nombre!r}")
                if p == nombre:
                    raise ValueError(f"auto dependencia en {nombre!r}")

        # Detección de ciclos (Kahn).
        dependientes = {n: set() for n in deps}
        grado = {n: len(ps) for n, ps in deps.items()}
        for n, ps in deps.items():
            for p in ps:
                dependientes[p].add(n)
        cola = [n for n, g in grado.items() if g == 0]
        visitados = 0
        while cola:
            n = cola.pop()
            visitados += 1
            for d in dependientes[n]:
                grado[d] -= 1
                if grado[d] == 0:
                    cola.append(d)
        if visitados != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._deps = deps
        self._dependientes = {n: frozenset(ds) for n, ds in dependientes.items()}
        self._estados = {n: PENDIENTE for n in sorted(deps)}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        try:
            estado = self._estados.get(nombre)
        except TypeError:
            raise ValueError(f"tarea desconocida: {nombre!r}") from None
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [n for n, e in self._estados.items() if e in (FALLO, BLOQUEADO)]
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if self._estados[d] == PENDIENTE:
                    self._estados[d] = BLOQUEADO
                    pila.append(d)
        return None

    def terminado(self):
        return all(e in (LISTO, FALLO, BLOQUEADO) for e in self._estados.values())
