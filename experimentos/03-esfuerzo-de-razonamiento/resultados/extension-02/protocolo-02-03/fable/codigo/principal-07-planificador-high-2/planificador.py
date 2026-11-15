"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


def _es_nombre(valor):
    return isinstance(valor, str) and valor != ""


class Planificador:
    """Administra el estado de tareas que dependen unas de otras."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia propia de la entrada: cada iterable se recorre una sola vez.
        prerrequisitos = {}
        try:
            pares = list(dependencias.items())
        except Exception as exc:
            raise ValueError("dependencias no se pudo recorrer") from exc
        for nombre, requeridas in pares:
            if not _es_nombre(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            try:
                requeridas = list(requeridas)
            except TypeError as exc:
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable"
                ) from exc
            for requerida in requeridas:
                if not _es_nombre(requerida):
                    raise ValueError(
                        f"nombre de dependencia inválido en {nombre!r}: "
                        f"{requerida!r}"
                    )
            prerrequisitos[nombre] = frozenset(requeridas)

        for nombre, requeridas in prerrequisitos.items():
            for requerida in requeridas:
                if requerida not in prerrequisitos:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: "
                        f"{requerida!r}"
                    )

        dependientes = {nombre: [] for nombre in prerrequisitos}
        for nombre, requeridas in prerrequisitos.items():
            for requerida in requeridas:
                dependientes[requerida].append(nombre)

        # Detección de ciclos (algoritmo de Kahn, sin recursión).
        faltantes = {n: len(reqs) for n, reqs in prerrequisitos.items()}
        libres = [n for n, cantidad in faltantes.items() if cantidad == 0]
        ordenadas = 0
        while libres:
            actual = libres.pop()
            ordenadas += 1
            for dependiente in dependientes[actual]:
                faltantes[dependiente] -= 1
                if faltantes[dependiente] == 0:
                    libres.append(dependiente)
        if ordenadas != len(prerrequisitos):
            raise ValueError("las dependencias contienen un ciclo")

        # Recién ahora se toca el objeto: una entrada inválida no lo altera.
        nombres = sorted(prerrequisitos)
        self._capacidad = int(capacidad)
        self._prerrequisitos = {n: prerrequisitos[n] for n in nombres}
        self._dependientes = {n: tuple(dependientes[n]) for n in nombres}
        self._estados = {n: PENDIENTE for n in nombres}
        self._en_curso = 0

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza las tareas habilitadas que entren en la capacidad libre."""
        lanzadas = []
        libres = self._capacidad - self._en_curso
        if libres <= 0:
            return lanzadas
        estados = self._estados
        # `_estados` está ordenado por nombre: el recorrido es lexicográfico.
        for nombre, estado in estados.items():
            if estado != PENDIENTE:
                continue
            if all(estados[r] == LISTO for r in self._prerrequisitos[nombre]):
                lanzadas.append(nombre)
                if len(lanzadas) == libres:
                    break
        for nombre in lanzadas:
            estados[nombre] = EN_CURSO
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como lista o fallida."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso "
                f"(estado: {self._estados[nombre]})"
            )

        self._en_curso -= 1
        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        por_visitar = [nombre]
        while por_visitar:
            actual = por_visitar.pop()
            for dependiente in self._dependientes[actual]:
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    por_visitar.append(dependiente)
        return None

    def terminado(self):
        """Indica si todas las tareas están en un estado final."""
        return all(estado in _FINALES for estado in self._estados.values())
