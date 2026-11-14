"""Planificador de dependencias que sólo administra estados."""

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
        for nombre, requisitos in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre inválido: {nombre!r}")
            if isinstance(requisitos, (str, bytes)) or isinstance(requisitos, Mapping):
                raise ValueError(f"dependencias inválidas para {nombre!r}")
            try:
                lista = list(requisitos)
            except TypeError:
                raise ValueError(f"dependencias inválidas para {nombre!r}") from None
            conjunto = set()
            for req in lista:
                if not _nombre_valido(req):
                    raise ValueError(f"nombre de dependencia inválido: {req!r}")
                conjunto.add(req)
            deps[nombre] = frozenset(conjunto)

        for nombre, reqs in deps.items():
            for req in reqs:
                if req not in deps:
                    raise ValueError(f"dependencia desconocida: {req!r} en {nombre!r}")
                if req == nombre:
                    raise ValueError(f"auto dependencia: {nombre!r}")

        # Detección de ciclos (iterativa, DFS con colores).
        BLANCO, GRIS, NEGRO = 0, 1, 2
        color = {n: BLANCO for n in deps}
        for inicio in sorted(deps):
            if color[inicio] != BLANCO:
                continue
            color[inicio] = GRIS
            pila = [(inicio, iter(sorted(deps[inicio])))]
            while pila:
                nodo, it = pila[-1]
                avanzo = False
                for sig in it:
                    if color[sig] == GRIS:
                        raise ValueError(f"ciclo detectado en {sig!r}")
                    if color[sig] == BLANCO:
                        color[sig] = GRIS
                        pila.append((sig, iter(sorted(deps[sig]))))
                        avanzo = True
                        break
                if not avanzo:
                    color[nodo] = NEGRO
                    pila.pop()

        dependientes = {n: set() for n in deps}
        for nombre, reqs in deps.items():
            for req in reqs:
                dependientes[req].add(nombre)

        self._deps = deps
        self._dependientes = {n: frozenset(s) for n, s in dependientes.items()}
        self._capacidad = capacidad
        self._estados = {n: PENDIENTE for n in deps}

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
            if all(self._estados[r] == LISTO for r in self._deps[nombre]):
                lanzadas.append(nombre)
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
        while pila:
            actual = pila.pop()
            for dep in self._dependientes[actual]:
                if self._estados[dep] == PENDIENTE:
                    self._estados[dep] = BLOQUEADO
                    pila.append(dep)
        return None

    def terminado(self):
        return all(e in (LISTO, FALLO, BLOQUEADO) for e in self._estados.values())
