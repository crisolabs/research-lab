"""Planificador de tareas con dependencias y capacidad limitada.

El módulo sólo administra estados: indica qué tareas pueden lanzarse y
registra cómo terminan. Ejecutarlas queda a cargo de quien lo usa.
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


def _str_puro(valor: object) -> str | None:
    """Devuelve ``valor`` como ``str`` puro, o ``None`` si no es un string."""
    tipo = type(valor)
    if tipo is str:
        return valor
    if issubclass(tipo, str):
        # Una subclase puede redefinir el hash o las comparaciones; se copia
        # su contenido para que el estado interno no dependa de ella.
        return str.__str__(valor)
    return None


def _validar_nombre(valor: object) -> str:
    """Devuelve el nombre de tarea como ``str`` puro o lanza ``ValueError``."""
    nombre = _str_puro(valor)
    if nombre is None:
        raise ValueError(
            f"nombre de tarea inválido: se esperaba str, no {type(valor).__name__}"
        )
    if not nombre:
        raise ValueError("nombre de tarea inválido: no puede ser vacío")
    return nombre


def _validar_capacidad(capacidad: object) -> int:
    """Devuelve la capacidad como ``int`` puro o lanza ``ValueError``."""
    tipo = type(capacidad)
    # bool es subclase de int, por eso se lo descarta de forma explícita.
    if tipo is bool or not issubclass(tipo, int):
        raise ValueError(
            f"capacidad debe ser un entero positivo, no {tipo.__name__}"
        )
    valor = int.__index__(capacidad)
    if valor <= 0:
        raise ValueError("capacidad debe ser un entero positivo")
    return valor


def _copiar_dependencias(dependencias: object) -> dict[str, tuple[str, ...]]:
    """Valida ``dependencias`` y devuelve una copia propia en orden canónico.

    En la copia tanto las tareas como los prerrequisitos de cada una quedan
    sin repeticiones y en orden lexicográfico, de modo que nada de lo que se
    calcule después dependa del orden de la entrada.
    """
    if not isinstance(dependencias, Mapping):
        raise ValueError(
            "dependencias debe ser un diccionario, no "
            + type(dependencias).__name__
        )
    conjuntos: dict[str, frozenset[str]] = {}
    for clave, valores in list(dependencias.items()):
        nombre = _validar_nombre(clave)
        if nombre in conjuntos:
            raise ValueError(f"nombre de tarea repetido: {nombre!r}")
        try:
            iterador = iter(valores)
        except TypeError:
            raise ValueError(
                f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
            ) from None
        conjuntos[nombre] = frozenset(_validar_nombre(valor) for valor in iterador)

    copia: dict[str, tuple[str, ...]] = {}
    for nombre in sorted(conjuntos):
        previos = tuple(sorted(conjuntos[nombre]))
        for previo in previos:
            if previo not in conjuntos:
                raise ValueError(
                    f"{nombre!r} depende de una tarea desconocida: {previo!r}"
                )
        copia[nombre] = previos
    return copia


def _buscar_ciclo(
    prerrequisitos: dict[str, tuple[str, ...]],
    dependientes: dict[str, list[str]],
) -> list[str] | None:
    """Devuelve un ciclo como lista de nombres, o ``None`` si no hay ninguno.

    En la lista cada tarea depende de la siguiente y la última repite a la
    primera; una auto dependencia es el ciclo ``[nombre, nombre]``.
    """
    # Orden topológico (Kahn): se retiran las tareas sin prerrequisitos por
    # resolver; las que no se pueden retirar están en un ciclo o dependen de él.
    restantes = {nombre: len(previos) for nombre, previos in prerrequisitos.items()}
    resueltas = [nombre for nombre, cantidad in restantes.items() if cantidad == 0]
    while resueltas:
        nombre = resueltas.pop()
        del restantes[nombre]
        for dependiente in dependientes[nombre]:
            restantes[dependiente] -= 1
            if restantes[dependiente] == 0:
                resueltas.append(dependiente)
    if not restantes:
        return None

    # Toda tarea restante tiene algún prerrequisito restante: siguiéndolos se
    # vuelve necesariamente a una tarea ya visitada, y ese tramo es un ciclo.
    camino: list[str] = []
    posiciones: dict[str, int] = {}
    actual = min(restantes)
    while actual not in posiciones:
        posiciones[actual] = len(camino)
        camino.append(actual)
        actual = next(
            previo for previo in prerrequisitos[actual] if previo in restantes
        )
    return camino[posiciones[actual]:] + [actual]


class Planificador:
    """Administra los estados de un conjunto de tareas con prerrequisitos.

    Una tarea puede lanzarse cuando todos sus prerrequisitos están listos y
    queda lugar libre: nunca hay más de ``capacidad`` tareas en curso.
    """

    def __init__(
        self, dependencias: Mapping[str, Iterable[str]], capacidad: int
    ) -> None:
        # Todo se valida y se arma en variables locales; los atributos se
        # asignan recién al final, así un argumento inválido nunca deja un
        # planificador a medio construir.
        capacidad = _validar_capacidad(capacidad)
        prerrequisitos = _copiar_dependencias(dependencias)
        dependientes: dict[str, list[str]] = {nombre: [] for nombre in prerrequisitos}
        for nombre, previos in prerrequisitos.items():
            for previo in previos:
                dependientes[previo].append(nombre)
        ciclo = _buscar_ciclo(prerrequisitos, dependientes)
        if ciclo is not None:
            raise ValueError(
                "ciclo de dependencias: " + " -> ".join(map(repr, ciclo))
            )
        habilitadas = [nombre for nombre, previos in prerrequisitos.items() if not previos]
        heapq.heapify(habilitadas)

        self._capacidad = capacidad
        self._estados = dict.fromkeys(prerrequisitos, _PENDIENTE)
        # Tareas que dependen directamente de cada una.
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        # Cantidad de prerrequisitos de cada tarea que todavía no están listos.
        self._faltantes = {
            nombre: len(previos) for nombre, previos in prerrequisitos.items()
        }
        # Montículo con las tareas pendientes a las que no les falta ningún
        # prerrequisito: su mínimo es la próxima tarea a lanzar.
        self._habilitadas = habilitadas
        self._en_curso = 0
        # Tareas pendientes o en curso; con cero, el planificador terminó.
        self._abiertas = len(prerrequisitos)

    def estados(self) -> dict[str, str]:
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self) -> list[str]:
        """Lanza tareas habilitadas mientras haya lugar y devuelve sus nombres.

        Se eligen en orden lexicográfico entre las pendientes cuyos
        prerrequisitos están todos listos, y pasan a estar en curso.
        """
        lanzadas: list[str] = []
        while self._habilitadas and self._en_curso < self._capacidad:
            nombre = heapq.heappop(self._habilitadas)
            self._estados[nombre] = _EN_CURSO
            self._en_curso += 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre: str, exito: bool = True) -> None:
        """Registra el final de una tarea en curso.

        Con éxito la tarea queda lista; si no, queda en fallo y se bloquean
        las tareas pendientes que dependen de ella, directa o transitivamente.
        Lanza ``ValueError``, sin cambiar nada, si ``exito`` no es bool o si
        la tarea no existe o no está en curso.
        """
        # Primero se valida todo: recién después se toca el estado.
        if type(exito) is not bool:
            raise ValueError(f"exito debe ser bool, no {type(exito).__name__}")
        clave = _str_puro(nombre)
        if clave is None:
            raise ValueError(
                f"tarea desconocida: se esperaba un nombre str, no {type(nombre).__name__}"
            )
        estado = self._estados.get(clave)
        if estado is None:
            raise ValueError(f"tarea desconocida: {clave!r}")
        if estado != _EN_CURSO:
            raise ValueError(
                f"la tarea {clave!r} no está en curso: su estado es {estado!r}"
            )

        self._en_curso -= 1
        self._abiertas -= 1
        if exito:
            self._estados[clave] = _LISTO
            # Una tarea bloqueada nunca llega a cero: el prerrequisito que la
            # bloqueó no va a estar listo. Las que llegan siguen pendientes.
            for dependiente in self._dependientes[clave]:
                self._faltantes[dependiente] -= 1
                if self._faltantes[dependiente] == 0:
                    heapq.heappush(self._habilitadas, dependiente)
        else:
            self._estados[clave] = _FALLO
            self._bloquear_dependientes(clave)

    def terminado(self) -> bool:
        """Indica si todas las tareas están en ``listo``, ``fallo`` o ``bloqueado``."""
        return self._abiertas == 0

    def _bloquear_dependientes(self, origen: str) -> None:
        """Bloquea las tareas pendientes que dependen de ``origen``."""
        # Quien depende de una tarea que no terminó bien nunca pudo lanzarse:
        # está pendiente o ya fue bloqueado junto con todos sus dependientes,
        # por lo que alcanza con avanzar a través de las tareas pendientes.
        por_revisar = [origen]
        while por_revisar:
            for dependiente in self._dependientes[por_revisar.pop()]:
                if self._estados[dependiente] == _PENDIENTE:
                    self._estados[dependiente] = _BLOQUEADO
                    self._abiertas -= 1
                    por_revisar.append(dependiente)
