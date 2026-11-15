"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: decide qué tareas pueden lanzarse y
registra cómo termina cada una. Ejecutarlas queda a cargo de quien lo usa.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable, Mapping

__all__ = ["Planificador"]

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"


def _como_nombre(valor: object) -> str | None:
    """Devuelve `valor` como `str` exacto si es un nombre válido; si no, `None`."""
    tipo = type(valor)
    if tipo is not str:
        if not issubclass(tipo, str):
            return None
        # Una subclase podría redefinir igualdad, hash u orden: se conserva
        # sólo el texto para que los nombres se comporten como strings puros.
        valor = str.__str__(valor)
    return valor or None


def _buscar_ciclo(requisitos_de: dict[str, set[str]], atascadas: set[str]) -> list[str]:
    """Devuelve un ciclo `a, b, ..., a` en el que cada tarea depende de la siguiente.

    `atascadas` son las tareas que el orden topológico no pudo ubicar. Cada
    una tiene al menos un prerrequisito atascado, así que seguirlos termina
    siempre repitiendo una tarea.
    """
    posicion: dict[str, int] = {}
    camino: list[str] = []
    actual = min(atascadas)
    while actual not in posicion:
        posicion[actual] = len(camino)
        camino.append(actual)
        actual = min(requisitos_de[actual] & atascadas)
    return camino[posicion[actual]:] + [actual]


class Planificador:
    """Administra los estados de un grafo de tareas con dependencias.

    Cada tarea está `pendiente`, `en_curso`, `listo`, `fallo` o `bloqueado`,
    y a lo sumo `capacidad` tareas están en curso al mismo tiempo.
    """

    def __init__(self, dependencias: Mapping[str, Iterable[str]], capacidad: int) -> None:
        tipo = type(capacidad)
        if tipo is bool or not issubclass(tipo, int):
            raise ValueError(
                f"capacidad debe ser un entero positivo, no {tipo.__name__}"
            )
        capacidad = int.__index__(capacidad)
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Primero se fijan las claves y recién después se recorren los
        # iterables, una sola vez cada uno porque pueden ser generadores.
        entradas: list[tuple[str, object]] = []
        requisitos_de: dict[str, set[str]] = {}
        for clave, valores in list(dependencias.items()):
            nombre = _como_nombre(clave)
            if nombre is None:
                raise ValueError("los nombres de tarea deben ser strings no vacíos")
            if nombre in requisitos_de:
                raise ValueError(f"nombre de tarea repetido: {nombre!r}")
            requisitos_de[nombre] = set()
            entradas.append((nombre, valores))

        for nombre, valores in entradas:
            try:
                iterador = iter(valores)
            except TypeError:
                raise ValueError(
                    f"las dependencias de {nombre!r} deben ser un iterable de nombres"
                ) from None
            requisitos = requisitos_de[nombre]
            for valor in iterador:
                requisito = _como_nombre(valor)
                if requisito is None:
                    raise ValueError(
                        f"las dependencias de {nombre!r} deben ser strings no vacíos"
                    )
                if requisito not in requisitos_de:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: {requisito!r}"
                    )
                requisitos.add(requisito)

        # Todo lo que sigue recorre los nombres ordenados, de modo que el
        # orden de entrada del diccionario no influye en nada.
        nombres = sorted(requisitos_de)
        faltan = {nombre: len(requisitos_de[nombre]) for nombre in nombres}
        dependientes: dict[str, list[str]] = {nombre: [] for nombre in nombres}
        for nombre in nombres:
            for requisito in requisitos_de[nombre]:
                dependientes[requisito].append(nombre)
        habilitadas = [nombre for nombre in nombres if not faltan[nombre]]

        # Orden topológico iterativo (Kahn): lo que no llega a ordenarse
        # forma parte de un ciclo o depende de uno.
        restantes = dict(faltan)
        pila = list(habilitadas)
        ordenadas = 0
        while pila:
            ordenadas += 1
            for dependiente in dependientes[pila.pop()]:
                restantes[dependiente] -= 1
                if not restantes[dependiente]:
                    pila.append(dependiente)
        if ordenadas != len(nombres):
            atascadas = {nombre for nombre in nombres if restantes[nombre]}
            ciclo = _buscar_ciclo(requisitos_de, atascadas)
            raise ValueError(
                "las dependencias forman un ciclo: " + " -> ".join(map(repr, ciclo))
            )

        # Recién acá se toca el objeto: una entrada inválida no deja rastros.
        self._capacidad = capacidad
        self._estados = dict.fromkeys(nombres, _PENDIENTE)
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        # Prerrequisitos de cada tarea que todavía no están `listo`.
        self._faltan = faltan
        # Montículo con las tareas pendientes a las que no les falta ninguno.
        # Todos sus ancestros están `listo`, así que nunca pueden bloquearse y
        # sólo salen de acá al ser lanzadas. Una lista ordenada ya es un
        # montículo válido.
        self._habilitadas = habilitadas
        self._en_curso = 0
        # Tareas que aún no llegaron a un estado final.
        self._abiertas = len(nombres)

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Lanza las tareas habilitadas que entren en la capacidad libre.

        Devuelve, en orden lexicográfico, sólo las lanzadas por esta llamada.
        """
        lanzadas: list[str] = []
        while self._en_curso < self._capacidad and self._habilitadas:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = _EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Registra el final de una tarea `en_curso`.

        Con éxito queda `listo`. Si no, queda `fallo` y se marca `bloqueado`
        todo lo pendiente que dependa de ella, directa o transitivamente.
        """
        # Se valida todo antes de modificar algo: un error no cambia nada.
        if type(exito) is not bool:
            raise ValueError(f"exito debe ser bool, no {type(exito).__name__}")
        clave = _como_nombre(nombre)
        estado = None if clave is None else self._estados.get(clave)
        if clave is None or estado is None:
            raise ValueError(
                "nombre de tarea inválido"
                if clave is None
                else f"tarea desconocida: {clave!r}"
            )
        if estado != _EN_CURSO:
            raise ValueError(
                f"la tarea {clave!r} no está en_curso (estado actual: {estado})"
            )

        self._en_curso -= 1
        self._abiertas -= 1
        if exito:
            self._estados[clave] = _LISTO
            for dependiente in self._dependientes[clave]:
                self._faltan[dependiente] -= 1
                # Llegar a cero implica que sigue pendiente: a una tarea
                # bloqueada siempre le falta el prerrequisito que la bloqueó.
                if not self._faltan[dependiente]:
                    heapq.heappush(self._habilitadas, dependiente)
            return

        self._estados[clave] = _FALLO
        # Lo que depende de una tarea que no llegó a `listo` nunca fue lanzado:
        # está pendiente o ya bloqueado. Lo ya bloqueado propagó su bloqueo
        # cuando lo recibió, así que alcanza con seguir desde lo que cambia.
        pila = [clave]
        while pila:
            for dependiente in self._dependientes[pila.pop()]:
                if self._estados[dependiente] == _PENDIENTE:
                    self._estados[dependiente] = _BLOQUEADO
                    self._abiertas -= 1
                    pila.append(dependiente)

    def terminado(self) -> bool:
        """Indica si todas las tareas están `listo`, `fallo` o `bloqueado`."""
        return self._abiertas == 0
