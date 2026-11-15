"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: no ejecuta tareas, no lanza threads ni
invoca callbacks. Quien lo usa pide trabajo con ``tomar()`` e informa cada
resultado con ``completar()``.
"""

import heapq
from collections.abc import Iterable, Mapping

__all__ = ["Planificador", "PENDIENTE", "EN_CURSO", "LISTO", "FALLO", "BLOQUEADO"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

# Tope de tareas que se nombran al informar un ciclo, para acotar el mensaje.
_MAX_NOMBRES_EN_CICLO = 10


class Planificador:
    """Administra los estados de un grafo acíclico de tareas.

    ``dependencias`` asocia cada tarea con sus prerrequisitos y ``capacidad``
    limita cuántas tareas pueden estar ``en_curso`` a la vez.
    """

    def __init__(
        self, dependencias: Mapping[str, Iterable[str]], capacidad: int
    ) -> None:
        capacidad = _validar_capacidad(capacidad)
        grafo = _copiar_grafo(dependencias)
        nombres = sorted(grafo)

        dependientes = {nombre: [] for nombre in nombres}
        for nombre in nombres:
            for prerrequisito in grafo[nombre]:
                dependientes[prerrequisito].append(nombre)
        _rechazar_ciclos(grafo, dependientes)

        # Recién acá, con todo validado, se toca el objeto.
        self._capacidad = capacidad
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = {nombre: len(grafo[nombre]) for nombre in nombres}
        self._estados = dict.fromkeys(nombres, PENDIENTE)
        # Heap con las tareas pendientes cuyos prerrequisitos están todos
        # listos. Una tarea así nunca puede bloquearse, de modo que sólo sale
        # de acá al ser lanzada. Una lista ordenada ya es un heap válido.
        self._habilitadas = [nombre for nombre in nombres if not grafo[nombre]]
        self._en_curso = 0
        self._sin_terminar = len(nombres)

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Lanza tareas habilitadas, en orden lexicográfico, hasta agotar los
        lugares libres, y devuelve la lista de las recién lanzadas."""
        lanzadas = []
        libres = self._capacidad - self._en_curso
        while libres > 0 and self._habilitadas:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            lanzadas.append(nombre)
            libres -= 1
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Registra el resultado de una tarea ``en_curso``.

        Con éxito queda ``listo``; si no, queda en ``fallo`` y se bloquean
        todas las tareas pendientes que dependen de ella, directa o
        transitivamente.
        """
        # Todas las validaciones van antes de la primera modificación.
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser un booleano")
        if not isinstance(nombre, str):
            raise ValueError(
                f"tarea desconocida (nombre de tipo {type(nombre).__name__})"
            )
        nombre = str.__str__(nombre)
        estado = self._estados.get(nombre)
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso (estado: {estado})"
            )

        self._en_curso -= 1
        self._sin_terminar -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                if self._faltantes[dependiente] == 0:
                    heapq.heappush(self._habilitadas, dependiente)
            return

        self._estados[nombre] = FALLO
        # Los descendientes de una tarea que estaba en curso sólo pueden estar
        # pendientes o ya bloqueados; en el segundo caso sus propios
        # descendientes se bloquearon antes y no hace falta recorrerlos.
        por_propagar = [nombre]
        while por_propagar:
            for dependiente in self._dependientes[por_propagar.pop()]:
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    self._sin_terminar -= 1
                    por_propagar.append(dependiente)

    def terminado(self) -> bool:
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return self._sin_terminar == 0


def _validar_capacidad(capacidad):
    """Devuelve la capacidad como ``int`` exacto o lanza ``ValueError``."""
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise ValueError("capacidad debe ser un entero positivo, no booleano")
    capacidad = int.__index__(capacidad)  # copia exacta aunque sea subclase
    if capacidad <= 0:
        raise ValueError(f"capacidad debe ser un entero positivo, no {capacidad}")
    return capacidad


def _normalizar_nombre(valor):
    """Devuelve el nombre como ``str`` exacto o lanza ``ValueError``."""
    if not isinstance(valor, str):
        raise ValueError(
            "los nombres de tarea deben ser strings no vacíos, "
            f"no {type(valor).__name__}"
        )
    nombre = str.__str__(valor)  # copia exacta aunque sea subclase
    if not nombre:
        raise ValueError("los nombres de tarea no pueden ser vacíos")
    return nombre


def _copiar_grafo(dependencias):
    """Valida la entrada y devuelve una copia propia nombre → prerrequisitos."""
    if not isinstance(dependencias, Mapping):
        raise ValueError("dependencias debe ser un diccionario")

    grafo = {}
    for clave, prerrequisitos in list(dependencias.items()):
        nombre = _normalizar_nombre(clave)
        if nombre in grafo:
            raise ValueError(f"tarea repetida: {nombre!r}")
        try:
            iterador = iter(prerrequisitos)
        except TypeError:
            raise ValueError(
                f"las dependencias de {nombre!r} deben ser un iterable de nombres"
            ) from None
        # Se recorre una sola vez: el iterable puede ser un generador.
        grafo[nombre] = frozenset(map(_normalizar_nombre, iterador))

    conocidas = grafo.keys()
    if not all(conocidas >= prerrequisitos for prerrequisitos in grafo.values()):
        # Se elige el primer caso en orden lexicográfico para que el mensaje
        # no dependa del orden de la entrada.
        nombre = min(n for n, previos in grafo.items() if not conocidas >= previos)
        desconocida = min(grafo[nombre] - conocidas)
        raise ValueError(
            f"{nombre!r} depende de una tarea desconocida: {desconocida!r}"
        )
    return grafo


def _rechazar_ciclos(grafo, dependientes):
    """Lanza ``ValueError`` si el grafo tiene algún ciclo (algoritmo de Kahn)."""
    grados = {nombre: len(prerrequisitos) for nombre, prerrequisitos in grafo.items()}
    libres = [nombre for nombre, grado in grados.items() if grado == 0]
    while libres:
        for dependiente in dependientes[libres.pop()]:
            grados[dependiente] -= 1
            if grados[dependiente] == 0:
                libres.append(dependiente)

    restantes = [nombre for nombre, grado in grados.items() if grado]
    if not restantes:
        return

    # Toda tarea restante tiene algún prerrequisito restante, así que siguiendo
    # esos enlaces se termina repitiendo una tarea: ese tramo es un ciclo.
    camino = []
    posiciones = {}
    actual = min(restantes)
    while actual not in posiciones:
        posiciones[actual] = len(camino)
        camino.append(actual)
        actual = min(p for p in grafo[actual] if grados[p])
    ciclo = camino[posiciones[actual]:]
    visibles = [repr(nombre) for nombre in ciclo[:_MAX_NOMBRES_EN_CICLO]]
    if len(ciclo) > _MAX_NOMBRES_EN_CICLO:
        visibles.append("...")
    visibles.append(repr(actual))
    raise ValueError("ciclo de dependencias: " + " -> ".join(visibles))
