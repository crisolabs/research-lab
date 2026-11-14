"""Planificador de tareas con dependencias (sólo administra estados)."""

from collections import deque
from collections.abc import Mapping

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"
_TERMINALES = frozenset({_LISTO, _FALLO, _BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


def _validar_grafo(dependencias):
    if not isinstance(dependencias, Mapping):
        raise ValueError("dependencias debe ser un diccionario")

    grafo = {}
    for nombre, prereqs in dependencias.items():
        _validar_nombre(nombre)
        if isinstance(prereqs, (str, bytes)):
            raise ValueError(f"prerrequisitos inválidos para {nombre!r}")
        try:
            elementos = list(prereqs)
        except TypeError:
            raise ValueError(f"prerrequisitos inválidos para {nombre!r}") from None
        for p in elementos:
            _validar_nombre(p)
        grafo[nombre] = frozenset(elementos)

    for nombre, prereqs in grafo.items():
        for p in prereqs:
            if p not in grafo:
                raise ValueError(f"referencia desconocida: {p!r} en {nombre!r}")

    _verificar_aciclico(grafo)
    return grafo


def _verificar_aciclico(grafo):
    # Algoritmo de Kahn: si no se pueden eliminar todos los nodos, hay ciclo.
    grados = {n: len(p) for n, p in grafo.items()}
    dependientes = {n: [] for n in grafo}
    for n, prereqs in grafo.items():
        for p in prereqs:
            dependientes[p].append(n)
    cola = deque(n for n, g in grados.items() if g == 0)
    eliminados = 0
    while cola:
        n = cola.popleft()
        eliminados += 1
        for d in dependientes[n]:
            grados[d] -= 1
            if grados[d] == 0:
                cola.append(d)
    if eliminados != len(grafo):
        raise ValueError("ciclo detectado en las dependencias")


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        grafo = _validar_grafo(dependencias)

        self._capacidad = capacidad
        self._prereqs = {n: frozenset(p) for n, p in sorted(grafo.items())}
        self._dependientes = {n: set() for n in self._prereqs}
        for n, prereqs in self._prereqs.items():
            for p in prereqs:
                self._dependientes[p].add(n)
        self._estados = {n: _PENDIENTE for n in self._prereqs}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == _EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != _PENDIENTE:
                continue
            if all(self._estados[p] == _LISTO for p in self._prereqs[nombre]):
                self._estados[nombre] = _EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != _EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en_curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = _LISTO
            return None

        self._estados[nombre] = _FALLO
        # Bloquea transitivamente todo lo pendiente que dependa del fallo.
        visitados = {nombre}
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for d in self._dependientes[actual]:
                if d in visitados:
                    continue
                visitados.add(d)
                if self._estados[d] == _PENDIENTE:
                    self._estados[d] = _BLOQUEADO
                cola.append(d)
        return None

    def terminado(self):
        return all(e in _TERMINALES for e in self._estados.values())
