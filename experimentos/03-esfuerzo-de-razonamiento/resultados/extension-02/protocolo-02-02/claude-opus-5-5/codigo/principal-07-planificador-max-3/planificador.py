"""Planificador de tareas con dependencias y capacidad acotada.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
Quien lo usa pide tareas con ``tomar()``, las ejecuta por su cuenta e informa
cada resultado con ``completar()``.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable, Mapping

__all__ = ["Planificador", "PENDIENTE", "EN_CURSO", "LISTO", "FALLO", "BLOQUEADO"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class _ErrorDeTipo(TypeError, ValueError):
    """Argumento de tipo incorrecto.

    Es un ``ValueError``, como pide el enunciado para toda entrada inválida, y a
    la vez un ``TypeError``, que es lo que describe.
    """


class Planificador:
    """Administra los estados de un grafo de tareas con capacidad acotada.

    ``dependencias`` asocia el nombre de cada tarea con sus prerrequisitos y
    ``capacidad`` es la cantidad máxima de tareas ``en_curso`` simultáneas.
    """

    def __init__(self, dependencias: Mapping[str, Iterable[str]], capacidad: int) -> None:
        capacidad = _validar_capacidad(capacidad)
        prerrequisitos = _copiar_dependencias(dependencias)
        # Al recorrer los nombres ordenados, cada lista de dependientes y el
        # diccionario de estados quedan en orden lexicográfico, sin importar el
        # orden de la entrada.
        nombres = sorted(prerrequisitos)
        dependientes: dict[str, list[str]] = {nombre: [] for nombre in nombres}
        for nombre in nombres:
            for requisito in prerrequisitos[nombre]:
                dependientes[requisito].append(nombre)
        _rechazar_ciclos(prerrequisitos, dependientes)

        self._capacidad = capacidad
        self._dependientes = {nombre: tuple(lista) for nombre, lista in dependientes.items()}
        self._estados = {nombre: PENDIENTE for nombre in nombres}
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = {nombre: len(prerrequisitos[nombre]) for nombre in nombres}
        # Montículo con las tareas pendientes cuyos prerrequisitos están listos.
        self._habilitadas = [nombre for nombre in nombres if not prerrequisitos[nombre]]
        heapq.heapify(self._habilitadas)
        self._en_curso = 0
        self._sin_terminar = len(nombres)

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Lanza tareas habilitadas en orden lexicográfico hasta llenar la capacidad.

        Devuelve las tareas lanzadas en esta llamada, ya marcadas ``en_curso``.
        """
        lanzadas: list[str] = []
        libres = self._capacidad - self._en_curso
        while len(lanzadas) < libres and self._habilitadas:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            lanzadas.append(nombre)
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Registra el resultado de una tarea ``en_curso``.

        Con éxito la marca ``listo``; si no, la marca ``fallo`` y bloquea toda
        tarea pendiente que dependa de ella directa o transitivamente.
        """
        if not isinstance(exito, bool):
            raise _ErrorDeTipo(f"exito debe ser bool, no {type(exito).__name__}")
        if not isinstance(nombre, str):
            raise _ErrorDeTipo(f"el nombre debe ser un string, no {type(nombre).__name__}")
        estado = self._estados.get(nombre)
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} está {estado}, no {EN_CURSO}")

        self._en_curso -= 1
        self._sin_terminar -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                habilitada = self._faltantes[dependiente] == 0
                if habilitada and self._estados[dependiente] == PENDIENTE:
                    heapq.heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            self._bloquear_dependientes(nombre)

    def terminado(self) -> bool:
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return self._sin_terminar == 0

    def _bloquear_dependientes(self, origen: str) -> None:
        """Bloquea las tareas pendientes que dependen transitivamente de ``origen``."""
        por_visitar = [origen]
        while por_visitar:
            for dependiente in self._dependientes[por_visitar.pop()]:
                # Una tarea ya bloqueada propagó el bloqueo cuando se la marcó.
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    self._sin_terminar -= 1
                    por_visitar.append(dependiente)


def _validar_capacidad(capacidad: object) -> int:
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise _ErrorDeTipo(f"la capacidad debe ser un entero, no {type(capacidad).__name__}")
    if capacidad <= 0:
        raise ValueError(f"la capacidad debe ser positiva, no {capacidad}")
    return int(capacidad)


def _validar_nombre(nombre: object, descripcion: str) -> None:
    if not isinstance(nombre, str):
        raise _ErrorDeTipo(f"{descripcion} debe ser un string, no {type(nombre).__name__}")
    if not nombre:
        raise ValueError(f"{descripcion} no puede ser vacío")


def _copiar_dependencias(dependencias: object) -> dict[str, frozenset[str]]:
    """Valida las dependencias y devuelve una copia propia, sin repeticiones."""
    if not isinstance(dependencias, Mapping):
        raise _ErrorDeTipo(
            f"las dependencias deben ser un diccionario, no {type(dependencias).__name__}"
        )
    entradas = list(dependencias.items())
    for nombre, _ in entradas:
        _validar_nombre(nombre, "el nombre de una tarea")
    conocidas = {nombre for nombre, _ in entradas}

    copia: dict[str, frozenset[str]] = {}
    for nombre, requisitos in entradas:
        try:
            iterador = iter(requisitos)
        except TypeError:
            raise _ErrorDeTipo(
                f"los prerrequisitos de {nombre!r} deben ser un iterable, "
                f"no {type(requisitos).__name__}"
            ) from None
        propios: set[str] = set()
        for requisito in iterador:
            _validar_nombre(requisito, f"un prerrequisito de {nombre!r}")
            if requisito not in conocidas:
                raise ValueError(f"{nombre!r} depende de {requisito!r}, que no es una tarea")
            propios.add(requisito)
        copia[nombre] = frozenset(propios)
    return copia


def _rechazar_ciclos(
    prerrequisitos: Mapping[str, frozenset[str]], dependientes: Mapping[str, list[str]]
) -> None:
    """Lanza ``ValueError`` si hay un ciclo (algoritmo de Kahn, sin recursión)."""
    faltantes = {nombre: len(requisitos) for nombre, requisitos in prerrequisitos.items()}
    por_visitar = [nombre for nombre, cantidad in faltantes.items() if cantidad == 0]
    while por_visitar:
        for dependiente in dependientes[por_visitar.pop()]:
            faltantes[dependiente] -= 1
            if faltantes[dependiente] == 0:
                por_visitar.append(dependiente)
    restantes = {nombre for nombre, cantidad in faltantes.items() if cantidad}
    if not restantes:
        return

    # Cada tarea restante está en un ciclo o depende de uno, así que tiene algún
    # prerrequisito también restante: siguiéndolos se termina cerrando un ciclo.
    camino: list[str] = []
    posiciones: dict[str, int] = {}
    actual = min(restantes)
    while actual not in posiciones:
        posiciones[actual] = len(camino)
        camino.append(actual)
        actual = min(r for r in prerrequisitos[actual] if r in restantes)
    ciclo = camino[posiciones[actual]:] + [actual]
    raise ValueError("ciclo de dependencias: " + " depende de ".join(map(repr, ciclo)))
