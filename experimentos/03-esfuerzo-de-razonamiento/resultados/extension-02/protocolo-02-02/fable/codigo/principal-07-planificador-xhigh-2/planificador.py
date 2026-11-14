"""Planificador de tareas con dependencias.

El módulo sólo administra estados: no lanza threads ni ejecuta callbacks.
"""

from collections.abc import Mapping
from heapq import heappop, heappush

__all__ = ["Planificador"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class _TipoInvalido(ValueError, TypeError):
    """Argumento de tipo incorrecto.

    Es un ``ValueError`` (lo que pide el contrato del módulo) y además un
    ``TypeError``, para quien prefiera atrapar los errores de tipo como tales.
    """


def _validar_nombre(nombre):
    if not isinstance(nombre, str):
        raise _TipoInvalido(f"nombre de tarea inválido (no es string): {nombre!r}")
    if not nombre:
        raise ValueError("nombre de tarea inválido: string vacío")


def _describir_ciclo(grafo, restantes):
    """Devuelve un ciclo concreto, como texto, entre las tareas ``restantes``.

    Toda tarea de ``restantes`` tiene al menos un prerrequisito en ``restantes``,
    así que seguir prerrequisitos desde cualquiera termina repitiendo una tarea.
    """
    actual = min(restantes)
    camino = []
    posiciones = {}
    while actual not in posiciones:
        posiciones[actual] = len(camino)
        camino.append(actual)
        actual = min(r for r in grafo[actual] if r in restantes)
    ciclo = camino[posiciones[actual]:] + [actual]
    return " -> ".join(repr(nombre) for nombre in ciclo)


class Planificador:
    """Administra el estado de un grafo de tareas con dependencias.

    ``dependencias`` asocia cada nombre de tarea con un iterable de nombres de
    prerrequisitos y ``capacidad`` es la cantidad máxima de tareas ``en_curso``
    al mismo tiempo.
    """

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _TipoInvalido(
                f"capacidad debe ser un entero positivo (no booleano): {capacidad!r}"
            )
        if capacidad <= 0:
            raise ValueError(f"capacidad debe ser un entero positivo: {capacidad!r}")
        if not isinstance(dependencias, Mapping):
            raise _TipoInvalido("dependencias debe ser un diccionario")

        # Copia propia del grafo: nombre -> conjunto de prerrequisitos.
        grafo = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            _validar_nombre(nombre)
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise _TipoInvalido(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from None
            requeridos = set()
            for requerido in iterador:
                _validar_nombre(requerido)
                requeridos.add(requerido)
            grafo[nombre] = requeridos

        nombres = sorted(grafo)
        for nombre in nombres:
            desconocidos = sorted(r for r in grafo[nombre] if r not in grafo)
            if desconocidos:
                raise ValueError(
                    f"{nombre!r} depende de una tarea desconocida: {desconocidos[0]!r}"
                )

        # Grafo inverso y cantidad de prerrequisitos que aún no están listos.
        dependientes = {nombre: [] for nombre in nombres}
        faltantes = {}
        for nombre in nombres:
            faltantes[nombre] = len(grafo[nombre])
            for requerido in grafo[nombre]:
                dependientes[requerido].append(nombre)

        # Detección de ciclos (Kahn): lo que no se puede ordenar está en un
        # ciclo o depende de uno. Cubre también la auto dependencia.
        grados = dict(faltantes)
        pila = [nombre for nombre in nombres if grados[nombre] == 0]
        while pila:
            for dependiente in dependientes[pila.pop()]:
                grados[dependiente] -= 1
                if grados[dependiente] == 0:
                    pila.append(dependiente)
        restantes = {nombre for nombre in nombres if grados[nombre] > 0}
        if restantes:
            raise ValueError(
                f"las dependencias tienen un ciclo: {_describir_ciclo(grafo, restantes)}"
            )

        self._capacidad = int(capacidad)
        self._estados = {nombre: PENDIENTE for nombre in nombres}
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        self._faltantes = faltantes
        # Heap de tareas pendientes con todos sus prerrequisitos listos. Una
        # tarea habilitada nunca se bloquea: todos sus prerrequisitos
        # (directos y transitivos) ya están listos. Una lista ordenada es un
        # heap válido.
        self._habilitadas = [nombre for nombre in nombres if faltantes[nombre] == 0]
        self._en_curso = 0
        # Tareas que todavía no están en un estado final (pendientes o en curso).
        self._abiertas = len(nombres)

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza tareas habilitadas, en orden lexicográfico, hasta llenar la capacidad.

        Devuelve la lista de las tareas recién lanzadas (posiblemente vacía).
        """
        libres = self._capacidad - self._en_curso
        lanzadas = []
        while libres > 0 and self._habilitadas:
            nombre = heappop(self._habilitadas)
            self._estados[nombre] = EN_CURSO
            self._en_curso += 1
            libres -= 1
            lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea ``en_curso``.

        Con éxito queda ``listo``; si no, queda ``fallo`` y se bloquean las
        tareas pendientes que dependen de ella directa o transitivamente.
        """
        # Toda la validación va antes de cualquier cambio de estado.
        if not isinstance(exito, bool):
            raise _TipoInvalido(f"exito debe ser bool: {exito!r}")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        estado = self._estados[nombre]
        if estado != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en_curso (estado actual: {estado})"
            )

        self._en_curso -= 1
        self._abiertas -= 1
        if exito:
            self._estados[nombre] = LISTO
            for dependiente in self._dependientes[nombre]:
                self._faltantes[dependiente] -= 1
                # Si llega a cero no puede estar bloqueada: ningún
                # prerrequisito suyo falló ni quedó bloqueado.
                if self._faltantes[dependiente] == 0:
                    heappush(self._habilitadas, dependiente)
        else:
            self._estados[nombre] = FALLO
            # Los dependientes (directos o transitivos) de una tarea que no
            # llegó a listo nunca fueron lanzados: están pendientes o ya
            # bloqueados. Si ya estaban bloqueados, sus dependientes también.
            pila = [nombre]
            while pila:
                for dependiente in self._dependientes[pila.pop()]:
                    if self._estados[dependiente] == PENDIENTE:
                        self._estados[dependiente] = BLOQUEADO
                        self._abiertas -= 1
                        pila.append(dependiente)

    def terminado(self):
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return self._abiertas == 0
