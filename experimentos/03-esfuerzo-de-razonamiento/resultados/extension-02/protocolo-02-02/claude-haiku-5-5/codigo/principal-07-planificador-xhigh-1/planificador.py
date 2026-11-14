"""Implementá el planificador pedido en TAREA.md."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINADOS = frozenset({LISTO, FALLO, BLOQUEADO})


def _nombre_valido(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Se valida y copia todo antes de asignar nada al objeto.
        requisitos = {}
        for nombre, prerrequisitos in dependencias.items():
            _nombre_valido(nombre)
            try:
                iterador = iter(prerrequisitos)
            except TypeError as exc:
                raise ValueError(f"prerrequisitos no iterables para {nombre!r}") from exc
            requisitos[nombre] = frozenset(_nombre_valido(p) for p in iterador)

        for nombre, reqs in requisitos.items():
            for r in reqs:
                if r not in requisitos:
                    raise ValueError(f"referencia desconocida: {nombre!r} depende de {r!r}")

        grados = {}
        dependientes = {n: [] for n in requisitos}
        for nombre, reqs in requisitos.items():
            grados[nombre] = len(reqs)
            for r in reqs:
                dependientes[r].append(nombre)

        # Orden topológico (Kahn): cualquier nodo sin resolver está en un ciclo.
        listos = [n for n, g in grados.items() if g == 0]
        resueltos = 0
        while listos:
            actual = listos.pop()
            resueltos += 1
            for d in dependientes[actual]:
                grados[d] -= 1
                if grados[d] == 0:
                    listos.append(d)
        if resueltos != len(requisitos):
            raise ValueError("ciclo de dependencias")

        self._capacidad = capacidad
        self._requisitos = requisitos
        self._dependientes = {n: tuple(ds) for n, ds in dependientes.items()}
        self._estados = {n: PENDIENTE for n in sorted(requisitos)}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        habilitadas = [
            n
            for n in self._estados
            if self._estados[n] == PENDIENTE
            and all(self._estados[r] == LISTO for r in self._requisitos[n])
        ]
        lanzadas = habilitadas[:libres]
        for n in lanzadas:
            self._estados[n] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en_curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        visitados = {nombre}
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if d in visitados:
                    continue
                visitados.add(d)
                if self._estados[d] == PENDIENTE:
                    self._estados[d] = BLOQUEADO
                pila.append(d)
        return None

    def terminado(self):
        return all(e in _TERMINADOS for e in self._estados.values())
