"""Planificador de dependencias.

Administra los estados de un grafo acíclico de tareas con un límite de tareas
simultáneas. No ejecuta nada: sólo decide qué tareas pueden lanzarse y registra
sus resultados.
"""

import heapq
import threading
from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _nombre(valor, descripcion):
    """Devuelve `valor` como `str` exacto o lanza `ValueError` si no es un nombre válido."""
    if not isinstance(valor, str):
        raise ValueError(
            f"{descripcion} debe ser un string, no {type(valor).__name__}"
        )
    texto = str.__str__(valor)
    if not texto:
        raise ValueError(f"{descripcion} no puede ser un string vacío")
    return texto


def _copiar_grafo(dependencias):
    """Valida `dependencias` y devuelve una copia propia: nombre -> frozenset de prerrequisitos."""
    if not isinstance(dependencias, Mapping):
        raise ValueError("dependencias debe ser un diccionario")

    grafo = {}
    for clave, valores in list(dependencias.items()):
        nombre = _nombre(clave, "el nombre de una tarea")
        if nombre in grafo:
            raise ValueError(f"nombre de tarea repetido: {nombre!r}")
        if isinstance(valores, (str, bytes, bytearray)):
            raise ValueError(
                f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres, "
                f"no {type(valores).__name__}"
            )
        try:
            iterador = iter(valores)
        except TypeError:
            raise ValueError(
                f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
            ) from None
        grafo[nombre] = frozenset(
            _nombre(valor, f"un prerrequisito de {nombre!r}") for valor in iterador
        )

    for nombre in sorted(grafo):
        desconocidos = sorted(grafo[nombre].difference(grafo))
        if desconocidos:
            raise ValueError(
                f"{nombre!r} depende de una tarea desconocida: {desconocidos[0]!r}"
            )
    return grafo


class Planificador:
    """Lleva el estado de un conjunto de tareas con dependencias y capacidad limitada."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero positivo")
        capacidad = int.__index__(capacidad)
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        grafo = _copiar_grafo(dependencias)
        nombres = sorted(grafo)

        dependientes = {nombre: [] for nombre in nombres}
        faltantes = {}
        for nombre in nombres:
            faltantes[nombre] = len(grafo[nombre])
            for previo in grafo[nombre]:
                dependientes[previo].append(nombre)

        # Orden topológico (Kahn): si no alcanza a todas las tareas, hay un ciclo.
        restantes = dict(faltantes)
        libres = [nombre for nombre in nombres if restantes[nombre] == 0]
        ordenadas = 0
        while libres:
            ordenadas += 1
            for dependiente in dependientes[libres.pop()]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    libres.append(dependiente)
        if ordenadas != len(nombres):
            ciclo = min(nombre for nombre in nombres if restantes[nombre] > 0)
            raise ValueError(f"las dependencias contienen un ciclo (ver {ciclo!r})")

        self._capacidad = capacidad
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        self._estados = {nombre: PENDIENTE for nombre in nombres}
        # Prerrequisitos de cada tarea que todavía no están `listo`.
        self._faltantes = faltantes
        # Heap con exactamente las tareas pendientes ya habilitadas.
        self._habilitadas = [nombre for nombre in nombres if faltantes[nombre] == 0]
        self._en_curso = 0
        # Tareas que aún no llegaron a un estado final.
        self._abiertas = len(nombres)
        self._candado = threading.Lock()

    def __getstate__(self):
        with self._candado:
            estado = {
                clave: valor
                for clave, valor in self.__dict__.items()
                if clave != "_candado"
            }
            for clave in ("_estados", "_faltantes", "_habilitadas"):
                estado[clave] = estado[clave].copy()
            return estado

    def __setstate__(self, estado):
        self.__dict__.update(estado)
        self._candado = threading.Lock()

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        with self._candado:
            return dict(self._estados)

    def tomar(self):
        """Lanza, en orden lexicográfico, las tareas habilitadas que entren en la capacidad libre."""
        with self._candado:
            lanzadas = []
            while self._habilitadas and self._en_curso < self._capacidad:
                nombre = heapq.heappop(self._habilitadas)
                self._estados[nombre] = EN_CURSO
                self._en_curso += 1
                lanzadas.append(nombre)
            return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea `en_curso`."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser un booleano")
        if not isinstance(nombre, str):
            raise ValueError(
                f"el nombre de la tarea debe ser un string, no {type(nombre).__name__}"
            )
        nombre = str.__str__(nombre)

        with self._candado:
            estado = self._estados.get(nombre)
            if estado is None:
                raise ValueError(f"tarea desconocida: {nombre!r}")
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
                    if self._faltantes[dependiente] == 0:
                        heapq.heappush(self._habilitadas, dependiente)
            else:
                self._estados[nombre] = FALLO
                # Todo lo que depende de un fallo sigue pendiente: nunca pudo lanzarse.
                por_propagar = [nombre]
                while por_propagar:
                    for dependiente in self._dependientes[por_propagar.pop()]:
                        if self._estados[dependiente] == PENDIENTE:
                            self._estados[dependiente] = BLOQUEADO
                            self._abiertas -= 1
                            por_propagar.append(dependiente)

    def terminado(self):
        """Indica si todas las tareas están `listo`, `fallo` o `bloqueado`."""
        with self._candado:
            return self._abiertas == 0
