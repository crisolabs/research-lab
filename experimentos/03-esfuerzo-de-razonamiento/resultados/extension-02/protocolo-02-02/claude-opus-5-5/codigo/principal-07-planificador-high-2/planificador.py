"""Planificador de dependencias con capacidad limitada."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


class _ErrorDeTipo(TypeError, ValueError):
    """Error de tipo que también es ValueError."""


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _ErrorDeTipo("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise _ErrorDeTipo("dependencias debe ser un diccionario")

        copia = {}
        for nombre, prereqs in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)):
                raise _ErrorDeTipo(
                    f"las dependencias de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                elementos = list(prereqs)
            except TypeError:
                raise _ErrorDeTipo(
                    f"las dependencias de {nombre!r} deben ser un iterable"
                ) from None
            conjunto = set()
            for dep in elementos:
                if not _nombre_valido(dep):
                    raise ValueError(f"nombre de dependencia inválido: {dep!r}")
                conjunto.add(dep)
            copia[nombre] = frozenset(conjunto)

        for nombre, prereqs in copia.items():
            for dep in prereqs:
                if dep not in copia:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {dep!r}"
                    )

        self._verificar_aciclico(copia)

        dependientes = {nombre: set() for nombre in copia}
        for nombre, prereqs in copia.items():
            for dep in prereqs:
                dependientes[dep].add(nombre)

        self._capacidad = capacidad
        self._deps = copia
        self._dependientes = {n: frozenset(d) for n, d in dependientes.items()}
        self._estados = {nombre: PENDIENTE for nombre in copia}

    @staticmethod
    def _verificar_aciclico(deps):
        # Algoritmo de Kahn: si quedan nodos sin procesar, hay un ciclo.
        grado = {nombre: len(prereqs) for nombre, prereqs in deps.items()}
        dependientes = {nombre: [] for nombre in deps}
        for nombre, prereqs in deps.items():
            for dep in prereqs:
                dependientes[dep].append(nombre)
        cola = [nombre for nombre, g in grado.items() if g == 0]
        procesados = 0
        while cola:
            actual = cola.pop()
            procesados += 1
            for siguiente in dependientes[actual]:
                grado[siguiente] -= 1
                if grado[siguiente] == 0:
                    cola.append(siguiente)
        if procesados != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[dep] == LISTO for dep in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if not isinstance(exito, bool):
            raise _ErrorDeTipo("exito debe ser bool")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        while pila:
            actual = pila.pop()
            for dependiente in self._dependientes[actual]:
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    pila.append(dependiente)
        return None

    def terminado(self):
        return all(e in _FINALES for e in self._estados.values())
