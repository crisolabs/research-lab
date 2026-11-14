"""Planificador de dependencias: administra los estados de un grafo de tareas."""

from collections import deque
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


def _nombre_valido(nombre):
    return isinstance(nombre, str) and len(nombre) > 0


class Planificador:
    """Administra tareas con prerrequisitos y una capacidad de ejecución."""

    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser positiva")

        try:
            items = list(dependencias.items())
        except TypeError as exc:
            raise ValueError("dependencias inválidas") from exc

        nombres = set()
        for nombre, _ in items:
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            nombres.add(nombre)

        prerrequisitos = {}
        for nombre, requisitos in items:
            if isinstance(requisitos, (str, bytes, bytearray)):
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                lista = list(requisitos)
            except TypeError as exc:
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} no son iterables"
                ) from exc
            conjunto = set()
            for requisito in lista:
                if not _nombre_valido(requisito):
                    raise ValueError(
                        f"prerrequisito inválido en {nombre!r}: {requisito!r}"
                    )
                if requisito not in nombres:
                    raise ValueError(
                        f"prerrequisito desconocido en {nombre!r}: {requisito!r}"
                    )
                if requisito == nombre:
                    raise ValueError(f"la tarea {nombre!r} depende de sí misma")
                conjunto.add(requisito)
            prerrequisitos[nombre] = frozenset(conjunto)

        dependientes = {nombre: set() for nombre in nombres}
        for nombre, requisitos in prerrequisitos.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        # Detección de ciclos (algoritmo de Kahn, sin recursión).
        grados = {nombre: len(reqs) for nombre, reqs in prerrequisitos.items()}
        cola = deque(nombre for nombre, grado in grados.items() if grado == 0)
        visitados = 0
        while cola:
            actual = cola.popleft()
            visitados += 1
            for dependiente in dependientes[actual]:
                grados[dependiente] -= 1
                if grados[dependiente] == 0:
                    cola.append(dependiente)
        if visitados != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._prerrequisitos = prerrequisitos
        self._dependientes = {n: frozenset(d) for n, d in dependientes.items()}
        self._estados = {nombre: PENDIENTE for nombre in sorted(nombres)}
        # Cantidad de prerrequisitos que todavía no están listos.
        self._faltantes = {n: len(r) for n, r in prerrequisitos.items()}
        # Tareas pendientes con todos sus prerrequisitos listos.
        self._habilitadas = {n for n, f in self._faltantes.items() if f == 0}
        self._en_curso = 0
        self._finalizadas = 0

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza tareas habilitadas en orden lexicográfico hasta llenar la capacidad."""
        libres = self._capacidad - self._en_curso
        if libres <= 0 or not self._habilitadas:
            return []
        lanzadas = sorted(self._habilitadas)[:libres]
        for nombre in lanzadas:
            self._habilitadas.discard(nombre)
            self._estados[nombre] = EN_CURSO
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista (éxito) o fallida."""
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso "
                f"(estado: {self._estados[nombre]})"
            )
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser un bool")

        self._en_curso -= 1
        self._finalizadas += 1

        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                if (
                    self._faltantes[dependiente] == 0
                    and self._estados[dependiente] == PENDIENTE
                ):
                    self._habilitadas.add(dependiente)
            return None

        self._estados[nombre] = FALLO
        cola = deque(self._dependientes[nombre])
        while cola:
            actual = cola.popleft()
            if self._estados[actual] != PENDIENTE:
                continue
            self._estados[actual] = BLOQUEADO
            self._habilitadas.discard(actual)
            self._finalizadas += 1
            cola.extend(self._dependientes[actual])
        return None

    def terminado(self):
        """Indica si todas las tareas están listas, fallidas o bloqueadas."""
        return self._finalizadas == len(self._estados)
