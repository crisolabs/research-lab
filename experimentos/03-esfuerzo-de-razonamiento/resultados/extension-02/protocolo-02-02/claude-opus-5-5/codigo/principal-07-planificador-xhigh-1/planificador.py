"""Planificador de dependencias: administra estados de tareas con prerrequisitos."""

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
    """Administra el avance de tareas con dependencias y capacidad limitada."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        copia = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prerrequisitos, (str, bytes, bytearray)):
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from None
            requeridos = set()
            for previo in iterador:
                if not _nombre_valido(previo):
                    raise ValueError(
                        f"nombre de prerrequisito inválido en {nombre!r}: {previo!r}"
                    )
                requeridos.add(previo)
            copia[nombre] = frozenset(requeridos)

        for nombre, requeridos in copia.items():
            for previo in requeridos:
                if previo not in copia:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {previo!r}"
                    )

        dependientes = {nombre: set() for nombre in copia}
        for nombre, requeridos in copia.items():
            for previo in requeridos:
                dependientes[previo].add(nombre)

        self._verificar_aciclico(copia, dependientes)

        orden = sorted(copia)
        self._capacidad = capacidad
        self._dependencias = {nombre: copia[nombre] for nombre in orden}
        self._dependientes = {
            nombre: tuple(sorted(dependientes[nombre])) for nombre in orden
        }
        self._estados = {nombre: PENDIENTE for nombre in orden}

    @staticmethod
    def _verificar_aciclico(dependencias, dependientes):
        faltantes = {nombre: len(req) for nombre, req in dependencias.items()}
        cola = deque(nombre for nombre, n in faltantes.items() if n == 0)
        procesadas = 0
        while cola:
            actual = cola.popleft()
            procesadas += 1
            for siguiente in dependientes[actual]:
                faltantes[siguiente] -= 1
                if faltantes[siguiente] == 0:
                    cola.append(siguiente)
        if procesadas != len(dependencias):
            raise ValueError("las dependencias contienen un ciclo")

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza tareas habilitadas en orden lexicográfico según la capacidad libre."""
        en_curso = sum(1 for estado in self._estados.values() if estado == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []
        lanzadas = []
        for nombre in self._estados:  # claves ya ordenadas lexicográficamente
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[previo] == LISTO for previo in self._dependencias[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista o fallida."""
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        visitadas = {nombre}
        cola = deque([nombre])
        while cola:
            actual = cola.popleft()
            for siguiente in self._dependientes[actual]:
                if siguiente in visitadas:
                    continue
                visitadas.add(siguiente)
                if self._estados[siguiente] == PENDIENTE:
                    self._estados[siguiente] = BLOQUEADO
                cola.append(siguiente)
        return None

    def terminado(self):
        """Indica si todas las tareas están listas, fallidas o bloqueadas."""
        return all(estado in _FINALES for estado in self._estados.values())
