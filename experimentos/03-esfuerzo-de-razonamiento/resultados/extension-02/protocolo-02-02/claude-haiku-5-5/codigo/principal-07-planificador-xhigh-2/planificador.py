"""Planificador de tareas con dependencias: administra sólo estados."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(valor):
    if not isinstance(valor, str):
        raise ValueError(f"nombre inválido: {valor!r}")
    nombre = str.__str__(valor)
    if not nombre:
        raise ValueError("nombre inválido: no puede ser vacío")
    return nombre


def _validar_capacidad(capacidad):
    if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad < 1:
        raise ValueError(f"capacidad debe ser un entero positivo: {capacidad!r}")
    return capacidad


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        capacidad = _validar_capacidad(capacidad)

        crudas = {}
        for clave, prerrequisitos in dependencias.items():
            nombre = _validar_nombre(clave)
            if isinstance(prerrequisitos, str):
                raise ValueError(f"las dependencias de {nombre!r} no pueden ser un str")
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(f"las dependencias de {nombre!r} no son iterables") from None
            crudas[nombre] = {_validar_nombre(p) for p in iterador}

        for nombre, prerrequisitos in crudas.items():
            desconocidos = sorted(p for p in prerrequisitos if p not in crudas)
            if desconocidos:
                raise ValueError(f"{nombre!r} referencia tareas desconocidas: {desconocidos}")

        prerrequisitos_por_tarea = {n: frozenset(crudas[n]) for n in sorted(crudas)}
        dependientes = {n: set() for n in prerrequisitos_por_tarea}
        for nombre, prerrequisitos in prerrequisitos_por_tarea.items():
            for p in prerrequisitos:
                dependientes[p].add(nombre)

        # Ordenamiento topológico (Kahn): si quedan tareas sin ordenar, hay ciclos.
        grados = {n: len(ps) for n, ps in prerrequisitos_por_tarea.items()}
        cola = [n for n, g in grados.items() if g == 0]
        ordenados = 0
        while cola:
            actual = cola.pop()
            ordenados += 1
            for d in dependientes[actual]:
                grados[d] -= 1
                if grados[d] == 0:
                    cola.append(d)
        if ordenados != len(grados):
            raise ValueError("las dependencias contienen ciclos")

        self._prerrequisitos = prerrequisitos_por_tarea
        self._dependientes = {n: frozenset(ds) for n, ds in dependientes.items()}
        self._estados = {n: PENDIENTE for n in prerrequisitos_por_tarea}
        self._capacidad = capacidad

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._prerrequisitos[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError(f"exito debe ser bool: {exito!r}")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        visitados = {nombre}
        pila = [nombre]
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
        return all(e in _TERMINALES for e in self._estados.values())
