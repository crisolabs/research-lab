"""Planificador de dependencias."""

from collections import deque
import heapq


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        nombres = list(dependencias.keys())
        for nombre in nombres:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres deben ser strings no vacíos")

        conocidos = set(nombres)
        requisitos = {}
        for nombre in nombres:
            try:
                iterador = iter(dependencias[nombre])
            except TypeError as error:
                raise ValueError("cada tarea debe tener un iterable de prerrequisitos") from error

            prerrequisitos = set()
            for prerrequisito in iterador:
                if not isinstance(prerrequisito, str) or not prerrequisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                if prerrequisito not in conocidos:
                    raise ValueError("referencia a una tarea desconocida")
                prerrequisitos.add(prerrequisito)
            requisitos[nombre] = frozenset(prerrequisitos)

        dependientes = {nombre: [] for nombre in nombres}
        pendientes = {}
        for nombre, prerrequisitos in requisitos.items():
            pendientes[nombre] = len(prerrequisitos)
            for prerrequisito in prerrequisitos:
                dependientes[prerrequisito].append(nombre)

        disponibles = [nombre for nombre, cantidad in pendientes.items() if cantidad == 0]
        heapq.heapify(disponibles)
        visitados = 0
        while disponibles:
            nombre = heapq.heappop(disponibles)
            visitados += 1
            for dependiente in dependientes[nombre]:
                pendientes[dependiente] -= 1
                if pendientes[dependiente] == 0:
                    heapq.heappush(disponibles, dependiente)
        if visitados != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._requisitos = requisitos
        self._dependientes = {
            nombre: tuple(lista) for nombre, lista in dependientes.items()
        }
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in nombres}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        en_curso = sum(estado == "en_curso" for estado in self._estados.values())
        lugares_libres = self._capacidad - en_curso
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(self._estados[requisito] == "listo" for requisito in self._requisitos[nombre])
        )
        nuevas = habilitadas[:lugares_libres]
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser booleano")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")

        if exito:
            self._estados[nombre] = "listo"
            return None

        self._estados[nombre] = "fallo"
        por_revisar = deque(self._dependientes[nombre])
        visitados = set()
        while por_revisar:
            dependiente = por_revisar.popleft()
            if dependiente in visitados:
                continue
            visitados.add(dependiente)
            if self._estados[dependiente] == "pendiente":
                self._estados[dependiente] = "bloqueado"
            por_revisar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        return all(estado in {"listo", "fallo", "bloqueado"} for estado in self._estados.values())
