"""Planificador de tareas con dependencias y capacidad de ejecución limitada.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable, Iterator, Mapping

__all__ = ["Planificador", "PENDIENTE", "EN_CURSO", "LISTO", "FALLO", "BLOQUEADO"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class Planificador:
    """Administra los estados de un grafo de tareas con una capacidad máxima.

    Todas las tareas empiezan pendientes. ``tomar()`` lanza, en orden
    lexicográfico, las pendientes cuyos prerrequisitos están todos listos;
    ``completar()`` registra el resultado de una tarea en curso. Un fallo
    bloquea a las tareas pendientes que dependen de él directa o
    transitivamente.
    """

    def __init__(
        self, dependencias: Mapping[str, Iterable[str]], capacidad: int
    ) -> None:
        capacidad = _validar_capacidad(capacidad)
        prerrequisitos = _copiar_dependencias(dependencias)
        nombres = sorted(prerrequisitos)
        # Recorriendo `nombres` en orden, cada lista de dependientes queda
        # ordenada y nada depende del orden de entrada del diccionario.
        dependientes: dict[str, list[str]] = {nombre: [] for nombre in nombres}
        for nombre in nombres:
            for prerrequisito in prerrequisitos[nombre]:
                dependientes[prerrequisito].append(nombre)
        _verificar_aciclico(prerrequisitos, dependientes)

        # Recién ahora, con todo validado, se modifica el objeto.
        self._capacidad = capacidad
        self._estados = {nombre: PENDIENTE for nombre in nombres}
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = {nombre: len(prerrequisitos[nombre]) for nombre in nombres}
        # Montículo con exactamente las tareas pendientes cuyos prerrequisitos
        # están todos listos (una lista ordenada ya es un montículo válido).
        self._habilitadas = [nombre for nombre in nombres if not prerrequisitos[nombre]]
        self._en_curso = 0
        self._sin_terminar = len(nombres)

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Lanza tareas habilitadas, en orden lexicográfico, hasta llenar la capacidad.

        Devuelve una lista nueva con las tareas que pasaron a ``en_curso``.
        """
        libres = self._capacidad - self._en_curso
        lanzadas: list[str] = []
        while len(lanzadas) < libres and self._habilitadas:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            lanzadas.append(nombre)
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Registra el resultado de una tarea en curso.

        Con éxito la marca ``listo``; si no, ``fallo``, y bloquea toda tarea
        pendiente que dependa de ella directa o transitivamente. Ante
        cualquier error lanza ``ValueError`` sin modificar nada.
        """
        if not isinstance(exito, bool):
            raise ValueError(f"exito debe ser bool, no {type(exito).__name__}")
        nombre = _como_nombre(nombre)
        estado = self._estados.get(nombre)
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(
                f"sólo se puede completar una tarea en_curso; {nombre!r} está {estado}"
            )

        self._en_curso -= 1
        self._sin_terminar -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                # Si ya no le falta nada, sigue pendiente: una tarea bloqueada
                # siempre tiene algún prerrequisito que nunca estará listo.
                if self._faltantes[dependiente] == 0:
                    heapq.heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            self._bloquear_dependientes(nombre)

    def terminado(self) -> bool:
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return self._sin_terminar == 0

    def _bloquear_dependientes(self, origen: str) -> None:
        pila = [origen]
        while pila:
            actual = pila.pop()
            for dependiente in self._dependientes[actual]:
                # Los dependientes de una tarea que nunca llegó a estar lista sólo
                # pueden estar pendientes o ya bloqueados; en este último caso sus
                # propios dependientes ya se bloquearon antes.
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                    self._sin_terminar -= 1
                    pila.append(dependiente)


def _validar_capacidad(capacidad: object) -> int:
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise ValueError(
            f"capacidad debe ser un entero positivo, no {type(capacidad).__name__}"
        )
    capacidad = int(capacidad)
    if capacidad <= 0:
        raise ValueError(f"capacidad debe ser un entero positivo, no {capacidad}")
    return capacidad


def _como_nombre(valor: object) -> str:
    """Valida un nombre de tarea y lo devuelve como ``str`` exacto."""
    if not isinstance(valor, str):
        raise ValueError(
            f"nombre de tarea inválido: se esperaba str, no {type(valor).__name__}"
        )
    # str.__str__ devuelve un str exacto aun para subclases de str, así el
    # estado interno no depende de __hash__/__eq__ redefinidos por el llamador.
    nombre = str.__str__(valor)
    if not nombre:
        raise ValueError("nombre de tarea inválido: no puede ser vacío")
    return nombre


def _copiar_dependencias(dependencias: object) -> dict[str, frozenset[str]]:
    """Copia el grafo validando nombres y referencias; ignora repeticiones."""
    if not isinstance(dependencias, Mapping):
        raise ValueError(
            f"dependencias debe ser un diccionario, no {type(dependencias).__name__}"
        )
    prerrequisitos: dict[str, frozenset[str]] = {}
    for clave, valor in list(dependencias.items()):
        nombre = _como_nombre(clave)
        if nombre in prerrequisitos:
            raise ValueError(f"tarea duplicada: {nombre!r}")
        prerrequisitos[nombre] = frozenset(
            map(_como_nombre, _iterar_prerrequisitos(nombre, valor))
        )
    for nombre in sorted(prerrequisitos):
        desconocidas = prerrequisitos[nombre].difference(prerrequisitos)
        if desconocidas:
            raise ValueError(
                f"la tarea {nombre!r} depende de tareas inexistentes: "
                + ", ".join(map(repr, sorted(desconocidas)))
            )
    return prerrequisitos


def _iterar_prerrequisitos(nombre: str, valor: object) -> Iterator[object]:
    # Un str también es iterable, pero leerlo como secuencia de caracteres
    # sería casi siempre un error del llamador, así que no se acepta.
    if not isinstance(valor, (str, bytes, bytearray)):
        try:
            return iter(valor)
        except TypeError:
            pass
    raise ValueError(
        f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres, "
        f"no {type(valor).__name__}"
    )


def _verificar_aciclico(
    prerrequisitos: Mapping[str, frozenset[str]],
    dependientes: Mapping[str, Iterable[str]],
) -> None:
    """Lanza ``ValueError`` si hay un ciclo (incluida la auto dependencia)."""
    # Algoritmo de Kahn, iterativo para no depender del límite de recursión. Al
    # terminar, `faltan` conserva sólo las tareas en un ciclo o que dependen de uno.
    faltan = {nombre: len(lista) for nombre, lista in prerrequisitos.items()}
    pila = [nombre for nombre, cantidad in faltan.items() if cantidad == 0]
    while pila:
        actual = pila.pop()
        del faltan[actual]
        for dependiente in dependientes[actual]:
            faltan[dependiente] -= 1
            if faltan[dependiente] == 0:
                pila.append(dependiente)
    if not faltan:
        return
    # Cada tarea que quedó tiene algún prerrequisito que también quedó, así que
    # siguiéndolos alguna se repite: eso da un ciclo concreto para el mensaje.
    camino: list[str] = []
    posicion: dict[str, int] = {}
    actual = min(faltan)
    while actual not in posicion:
        posicion[actual] = len(camino)
        camino.append(actual)
        actual = min(p for p in prerrequisitos[actual] if p in faltan)
    ciclo = camino[posicion[actual]:] + [actual]
    raise ValueError(
        "dependencias cíclicas (cada tarea depende de la siguiente): "
        + " -> ".join(map(repr, ciclo))
    )
