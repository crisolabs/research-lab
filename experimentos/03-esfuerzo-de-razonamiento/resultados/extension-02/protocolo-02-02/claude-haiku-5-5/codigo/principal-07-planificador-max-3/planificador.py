"""Implementá el planificador pedido en TAREA.md."""

from collections import deque
from collections.abc import Mapping

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"
_TERMINALES = frozenset({_LISTO, _FALLO, _BLOQUEADO})


def _nombre_valido(valor):
    if not isinstance(valor, str):
        raise ValueError(f"nombre inválido: {valor!r}")
    # Copia a str base: no ejecuta métodos de subclases del usuario.
    nombre = str.__str__(valor)
    if not nombre:
        raise ValueError("nombre inválido: no puede ser vacío")
    return nombre


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError(f"capacidad inválida: {capacidad!r}")
        capacidad = int.__int__(capacidad)
        if capacidad <= 0:
            raise ValueError(f"capacidad inválida: {capacidad!r}")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        grafo = {}
        for clave, valor in list(dependencias.items()):
            nombre = _nombre_valido(clave)
            if nombre in grafo:
                raise ValueError(f"nombre duplicado: {nombre!r}")
            try:
                iterable = iter(valor)
            except TypeError:
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}") from None
            grafo[nombre] = {_nombre_valido(p) for p in iterable}

        for nombre, prerrequisitos in grafo.items():
            for p in prerrequisitos:
                if p not in grafo:
                    raise ValueError(
                        f"referencia desconocida: {nombre!r} depende de {p!r}"
                    )

        dependientes = {n: set() for n in grafo}
        for nombre, prerrequisitos in grafo.items():
            for p in prerrequisitos:
                dependientes[p].add(nombre)

        # Kahn: sólo quedan tareas sin ordenar si hay ciclo (incluye auto dependencia).
        faltantes = {n: len(p) for n, p in grafo.items()}
        cola = deque(n for n, k in faltantes.items() if k == 0)
        ordenadas = 0
        while cola:
            actual = cola.popleft()
            ordenadas += 1
            for d in dependientes[actual]:
                faltantes[d] -= 1
                if faltantes[d] == 0:
                    cola.append(d)
        if ordenadas != len(grafo):
            raise ValueError("ciclo en las dependencias")

        nombres = sorted(grafo)
        self._capacidad = capacidad
        self._prerrequisitos = {n: frozenset(grafo[n]) for n in nombres}
        self._dependientes = {n: frozenset(dependientes[n]) for n in nombres}
        self._estados = {n: _PENDIENTE for n in nombres}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == _EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        habilitadas = sorted(
            n
            for n, e in self._estados.items()
            if e == _PENDIENTE
            and all(self._estados[p] == _LISTO for p in self._prerrequisitos[n])
        )
        lanzadas = habilitadas[:libres]
        for n in lanzadas:
            self._estados[n] = _EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        nombre = _nombre_valido(nombre)
        if nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != _EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError(f"exito debe ser bool: {exito!r}")

        if exito:
            self._estados[nombre] = _LISTO
            return None

        self._estados[nombre] = _FALLO
        pila = [nombre]
        visitadas = {nombre}
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if d in visitadas:
                    continue
                visitadas.add(d)
                if self._estados[d] == _PENDIENTE:
                    self._estados[d] = _BLOQUEADO
                pila.append(d)
        return None

    def terminado(self):
        return all(e in _TERMINALES for e in self._estados.values())
