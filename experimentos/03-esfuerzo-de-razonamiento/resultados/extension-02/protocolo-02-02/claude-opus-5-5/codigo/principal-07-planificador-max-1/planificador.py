"""Planificador de tareas con dependencias.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable, Iterator, Mapping
from typing import Any

__all__ = ["Planificador", "PENDIENTE", "EN_CURSO", "LISTO", "FALLO", "BLOQUEADO"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _es_nombre_valido(nombre: object) -> bool:
    return isinstance(nombre, str) and nombre != ""


def _iterador_de_requisitos(requisitos: Any) -> Iterator[object] | None:
    """Devuelve un iterador sobre ``requisitos`` o ``None`` si no es aceptable.
    Los strings se rechazan: son iterables de caracteres, no de nombres."""
    if isinstance(requisitos, (str, bytes, bytearray)):
        return None
    try:
        return iter(requisitos)
    except TypeError:
        return None


def _copiar_dependencias(dependencias: object) -> dict[str, set[str]]:
    """Valida ``dependencias`` y devuelve una copia propia (sin repeticiones),
    con las tareas en orden lexicográfico."""
    if not isinstance(dependencias, Mapping):
        raise ValueError(
            f"las dependencias deben ser un diccionario, no {type(dependencias).__name__}"
        )
    # Instantánea de la entrada: cada iterable de prerrequisitos se recorre una sola vez.
    entradas = list(dependencias.items())
    for nombre, _ in entradas:
        if not _es_nombre_valido(nombre):
            raise ValueError(f"nombre de tarea inválido: {nombre!r}")
    entradas.sort(key=lambda entrada: entrada[0])

    copia: dict[str, set[str]] = {}
    for nombre, requisitos in entradas:
        iterador = _iterador_de_requisitos(requisitos)
        if iterador is None:
            raise ValueError(
                f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres, "
                f"no {type(requisitos).__name__}"
            )
        unicos: set[str] = set()
        for requisito in iterador:
            if not _es_nombre_valido(requisito):
                raise ValueError(f"prerrequisito inválido en {nombre!r}: {requisito!r}")
            unicos.add(requisito)
        copia[nombre] = unicos

    for nombre, requisitos in copia.items():
        if nombre in requisitos:
            raise ValueError(f"la tarea {nombre!r} depende de sí misma")
        if not requisitos <= copia.keys():
            desconocido = min(requisitos - copia.keys())
            raise ValueError(f"la tarea {nombre!r} depende de {desconocido!r}, que no existe")
    return copia


def _verificar_aciclico(
    prerrequisitos: Mapping[str, set[str]],
    dependientes: Mapping[str, Iterable[str]],
) -> None:
    """Lanza ``ValueError`` si el grafo tiene un ciclo (algoritmo de Kahn)."""
    faltantes = {nombre: len(requisitos) for nombre, requisitos in prerrequisitos.items()}
    pila = [nombre for nombre, cantidad in faltantes.items() if cantidad == 0]
    while pila:
        for dependiente in dependientes[pila.pop()]:
            faltantes[dependiente] -= 1
            if faltantes[dependiente] == 0:
                pila.append(dependiente)
    trabadas = {nombre for nombre, cantidad in faltantes.items() if cantidad > 0}
    if not trabadas:
        return
    # Toda tarea trabada tiene algún prerrequisito trabado: siguiéndolos
    # se repite una tarea, y el tramo entre las repeticiones es un ciclo.
    recorrido: list[str] = []
    posiciones: dict[str, int] = {}
    actual = min(trabadas)
    while actual not in posiciones:
        posiciones[actual] = len(recorrido)
        recorrido.append(actual)
        actual = min(prerrequisitos[actual] & trabadas)
    ciclo = recorrido[posiciones[actual]:] + [actual]
    raise ValueError(
        "ciclo de dependencias (cada tarea depende de la siguiente): "
        + " -> ".join(map(repr, ciclo))
    )


class Planificador:
    """Administra los estados de tareas con prerrequisitos, con a lo sumo
    ``capacidad`` tareas ``en_curso`` a la vez."""

    def __init__(self, dependencias: Mapping[str, Iterable[str]], capacidad: int) -> None:
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError(
                f"la capacidad debe ser un entero positivo (no booleano): {capacidad!r}"
            )
        prerrequisitos = _copiar_dependencias(dependencias)
        dependientes: dict[str, list[str]] = {nombre: [] for nombre in prerrequisitos}
        for nombre, requisitos in prerrequisitos.items():
            for requisito in requisitos:
                dependientes[requisito].append(nombre)
        _verificar_aciclico(prerrequisitos, dependientes)

        self._capacidad = int(capacidad)
        self._dependientes = dependientes
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = {nombre: len(reqs) for nombre, reqs in prerrequisitos.items()}
        self._estados = {nombre: PENDIENTE for nombre in prerrequisitos}
        # Montículo de tareas pendientes con todos sus prerrequisitos listos.
        self._habilitadas = [n for n, cantidad in self._faltantes.items() if cantidad == 0]
        heapq.heapify(self._habilitadas)
        self._en_curso = 0
        self._sin_terminar = len(self._estados)  # pendientes + en curso

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Marca ``en_curso`` las tareas habilitadas, en orden lexicográfico,
        hasta llenar la capacidad libre, y devuelve las recién lanzadas."""
        lanzadas: list[str] = []
        while self._habilitadas and self._en_curso < self._capacidad:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Termina una tarea ``en_curso``: con éxito queda ``listo``; si no, queda
        ``fallo`` y se bloquean las pendientes que dependen de ella."""
        if not isinstance(exito, bool):
            raise ValueError(f"exito debe ser bool, no {type(exito).__name__}")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        estado = self._estados[nombre]
        if estado != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso (está {estado})")

        self._en_curso -= 1
        self._sin_terminar -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                if self._faltantes[dependiente] == 0 and self._estados[dependiente] == PENDIENTE:
                    heapq.heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            self._bloquear_dependientes(nombre)

    def terminado(self) -> bool:
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return self._sin_terminar == 0

    def _bloquear_dependientes(self, origen: str) -> None:
        """Bloquea toda tarea pendiente que depende, directa o transitivamente,
        de ``origen``. Las ya bloqueadas no se recorren: sus dependientes ya
        quedaron bloqueados cuando se las bloqueó."""
        pila = [origen]
        while pila:
            for dependiente in self._dependientes[pila.pop()]:
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    self._sin_terminar -= 1
                    pila.append(dependiente)
