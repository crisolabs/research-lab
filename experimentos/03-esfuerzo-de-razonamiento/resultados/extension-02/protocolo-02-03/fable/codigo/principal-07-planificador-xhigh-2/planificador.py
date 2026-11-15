"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

from collections.abc import Mapping
from heapq import heappop, heappush

__all__ = ["Planificador", "PENDIENTE", "EN_CURSO", "LISTO", "FALLO", "BLOQUEADO"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _nombre_valido(nombre):
    """Devuelve `nombre` como `str` exacto, o lanza `ValueError` si no es válido."""
    if not isinstance(nombre, str):
        raise ValueError(f"nombre de tarea inválido: {nombre!r}")
    # Las subclases de str se copian a un str puro: así el estado interno no
    # depende de objetos (ni de comparaciones) que controle quien llama.
    texto = nombre if type(nombre) is str else str.__str__(nombre)
    if not texto:
        raise ValueError("nombre de tarea inválido: string vacío")
    return texto


class Planificador:
    """Administra el estado de tareas con prerrequisitos y un tope de tareas en curso."""

    __slots__ = (
        "_capacidad",
        "_estados",
        "_dependientes",
        "_faltantes",
        "_habilitadas",
        "_en_curso",
        "_abiertas",
    )

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo (no booleano)")
        capacidad = int.__index__(capacidad)  # int puro aunque venga una subclase
        if capacidad < 1:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia validada de la entrada: nombre -> conjunto de prerrequisitos.
        grafo = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            nombre = _nombre_valido(nombre)
            if nombre in grafo:
                raise ValueError(f"nombre de tarea repetido: {nombre!r}")
            if isinstance(prerrequisitos, (str, bytes, bytearray)):
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable "
                    f"de nombres, no {type(prerrequisitos).__name__}"
                )
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from None
            grafo[nombre] = {_nombre_valido(p) for p in iterador}

        orden = sorted(grafo)
        for nombre in orden:
            desconocidas = [p for p in grafo[nombre] if p not in grafo]
            if desconocidas:
                raise ValueError(
                    f"{nombre!r} depende de una tarea desconocida: {min(desconocidas)!r}"
                )

        dependientes = {nombre: [] for nombre in orden}
        for nombre in orden:
            for prerrequisito in grafo[nombre]:
                dependientes[prerrequisito].append(nombre)
        faltantes = {nombre: len(grafo[nombre]) for nombre in orden}
        # Una lista ordenada ya es un heap válido.
        habilitadas = [nombre for nombre in orden if not faltantes[nombre]]

        # Detección de ciclos (Kahn, iterativo): si no se puede visitar todo
        # el grafo respetando las dependencias, hay un ciclo.
        restantes = dict(faltantes)
        pila = list(habilitadas)
        visitadas = 0
        while pila:
            visitadas += 1
            for dependiente in dependientes[pila.pop()]:
                restantes[dependiente] -= 1
                if not restantes[dependiente]:
                    pila.append(dependiente)
        if visitadas != len(orden):
            # Toda tarea no visitada tiene algún prerrequisito no visitado;
            # siguiéndolos necesariamente se cierra un ciclo.
            actual = next(nombre for nombre in orden if restantes[nombre])
            camino, posicion = [], {}
            while actual not in posicion:
                posicion[actual] = len(camino)
                camino.append(actual)
                actual = min(p for p in grafo[actual] if restantes[p])
            ciclo = camino[posicion[actual]:] + [actual]
            raise ValueError(
                "ciclo de dependencias: " + " -> ".join(repr(n) for n in ciclo)
            )

        # Recién acá, con todo validado, se toca el objeto.
        self._capacidad = capacidad
        self._estados = dict.fromkeys(orden, PENDIENTE)
        self._dependientes = {n: tuple(ds) for n, ds in dependientes.items()}
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = faltantes
        # Heap de tareas pendientes con todos sus prerrequisitos listos.
        self._habilitadas = habilitadas
        self._en_curso = 0
        # Tareas pendientes o en curso (es decir, sin estado final).
        self._abiertas = len(orden)

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza tareas habilitadas, en orden lexicográfico, hasta llenar la capacidad.

        Devuelve la lista de tareas recién lanzadas (posiblemente vacía).
        """
        lanzadas = []
        while self._habilitadas and self._en_curso < self._capacidad:
            nombre = heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea en curso.

        Con éxito queda `listo`; si no, queda `fallo` y se bloquean todas las
        tareas pendientes que dependan de ella directa o transitivamente.
        """
        # Todas las validaciones van antes de cualquier cambio de estado.
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        try:
            nombre = _nombre_valido(nombre)
            estado = self._estados[nombre]
        except (ValueError, KeyError):
            raise ValueError(f"tarea desconocida: {nombre!r}") from None
        if estado != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso (estado: {estado})"
            )

        self._en_curso -= 1
        self._abiertas -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                if (
                    not self._faltantes[dependiente]
                    and self._estados[dependiente] == PENDIENTE
                ):
                    heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            # Una tarea ya bloqueada tiene bloqueados a todos sus descendientes,
            # así que alcanza con propagar a través de las recién bloqueadas.
            pila = [nombre]
            while pila:
                for dependiente in self._dependientes[pila.pop()]:
                    if self._estados[dependiente] == PENDIENTE:
                        self._estados[dependiente] = BLOQUEADO
                        self._abiertas -= 1
                        pila.append(dependiente)
        return None

    def terminado(self):
        """Indica si todas las tareas están en un estado final."""
        return self._abiertas == 0
