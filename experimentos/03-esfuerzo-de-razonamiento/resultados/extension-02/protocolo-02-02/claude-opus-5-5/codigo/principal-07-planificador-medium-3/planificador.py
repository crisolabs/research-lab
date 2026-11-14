"""Planificador de dependencias que sólo administra estados."""

from collections.abc import Mapping

__all__ = ["Planificador"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


class _ErrorEntrada(ValueError, TypeError):
    """Error de entrada inválida (compatible con ValueError y TypeError)."""


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _ErrorEntrada("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise _ErrorEntrada("dependencias debe ser un diccionario")

        copia = {}
        for nombre, prereqs in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)) or isinstance(prereqs, Mapping):
                raise _ErrorEntrada(f"prerrequisitos inválidos para {nombre!r}")
            try:
                elementos = list(prereqs)
            except TypeError:
                raise _ErrorEntrada(f"prerrequisitos de {nombre!r} no son iterables") from None
            vistos = set()
            for p in elementos:
                if not _nombre_valido(p):
                    raise ValueError(f"prerrequisito inválido: {p!r}")
                vistos.add(p)
            copia[nombre] = frozenset(vistos)

        for nombre, prereqs in copia.items():
            for p in prereqs:
                if p not in copia:
                    raise ValueError(f"referencia desconocida: {p!r} en {nombre!r}")

        self._verificar_ciclos(copia)

        self._deps = copia
        dependientes = {n: set() for n in copia}
        for nombre, prereqs in copia.items():
            for p in prereqs:
                dependientes[p].add(nombre)
        self._dependientes = {n: frozenset(s) for n, s in dependientes.items()}
        self._capacidad = capacidad
        self._estados = {n: PENDIENTE for n in copia}
        self._en_curso = 0

    @staticmethod
    def _verificar_ciclos(grafo):
        # DFS iterativo con colores: 0 blanco, 1 gris, 2 negro.
        color = dict.fromkeys(grafo, 0)
        for inicio in sorted(grafo):
            if color[inicio]:
                continue
            color[inicio] = 1
            pila = [(inicio, iter(sorted(grafo[inicio])))]
            while pila:
                nodo, it = pila[-1]
                siguiente = next(it, None)
                if siguiente is None:
                    color[nodo] = 2
                    pila.pop()
                elif color[siguiente] == 1:
                    raise ValueError(f"ciclo detectado en {siguiente!r}")
                elif color[siguiente] == 0:
                    color[siguiente] = 1
                    pila.append((siguiente, iter(sorted(grafo[siguiente]))))

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        libres = self._capacidad - self._en_curso
        if libres <= 0:
            return []
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise _ErrorEntrada("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        self._en_curso -= 1
        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        while pila:
            actual = pila.pop()
            for dep in self._dependientes[actual]:
                if self._estados[dep] == PENDIENTE:
                    self._estados[dep] = BLOQUEADO
                    pila.append(dep)
        return None

    def terminado(self):
        return all(e in _FINALES for e in self._estados.values())
