"""Planificador de dependencias: sólo administra estados, sin threads ni callbacks."""

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
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        # Copia profunda de la entrada: nombre -> frozenset de prerrequisitos.
        copia = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            _validar_nombre(nombre)
            try:
                prerrequisitos = list(prerrequisitos)
            except TypeError:
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}") from None
            copia[nombre] = frozenset(_validar_nombre(p) for p in prerrequisitos)

        for nombre, prerrequisitos in copia.items():
            for p in prerrequisitos:
                if p not in copia:
                    raise ValueError(f"referencia desconocida: {nombre!r} -> {p!r}")

        # Detección de ciclos (Kahn). La auto dependencia nunca llega a 0 y queda como ciclo.
        restantes = {n: len(p) for n, p in copia.items()}
        dependientes = {n: set() for n in copia}
        for nombre, prerrequisitos in copia.items():
            for p in prerrequisitos:
                dependientes[p].add(nombre)
        cola = deque(n for n, c in restantes.items() if c == 0)
        procesados = 0
        while cola:
            actual = cola.popleft()
            procesados += 1
            for d in dependientes[actual]:
                restantes[d] -= 1
                if restantes[d] == 0:
                    cola.append(d)
        if procesados != len(copia):
            raise ValueError("ciclo de dependencias")

        self._prerrequisitos = copia
        self._dependientes = {n: frozenset(s) for n, s in dependientes.items()}
        self._estados = {n: PENDIENTE for n in copia}
        self._capacidad = capacidad

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        libres = self._capacidad - sum(1 for e in self._estados.values() if e == EN_CURSO)
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._prerrequisitos[nombre]):
                self._estados[nombre] = EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en_curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for d in self._dependientes[actual]:
                if self._estados[d] == PENDIENTE:
                    self._estados[d] = BLOQUEADO
                    cola.append(d)
        return None

    def terminado(self):
        return all(e in _TERMINALES for e in self._estados.values())
