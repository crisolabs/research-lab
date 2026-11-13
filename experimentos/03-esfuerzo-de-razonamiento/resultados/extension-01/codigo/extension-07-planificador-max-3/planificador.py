from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("La capacidad debe ser un entero positivo.")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario.")

        entradas = dependencias.copy()
        if any(not isinstance(nombre, str) or not nombre for nombre in entradas):
            raise ValueError("Los nombres deben ser strings no vacíos.")

        grafo = {}
        for nombre, requisitos in entradas.items():
            try:
                requisitos = frozenset(requisitos)
            except TypeError as error:
                raise ValueError(
                    "Los prerrequisitos deben ser iterables de nombres."
                ) from error
            if any(not isinstance(requisito, str) or not requisito
                   for requisito in requisitos):
                raise ValueError("Los nombres deben ser strings no vacíos.")
            if not requisitos.issubset(entradas):
                raise ValueError("Todos los prerrequisitos deben existir.")
            grafo[nombre] = requisitos

        dependientes = {nombre: set() for nombre in grafo}
        restantes = {}
        for nombre, requisitos in grafo.items():
            restantes[nombre] = len(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        habilitadas = deque(
            nombre for nombre, cantidad in restantes.items() if cantidad == 0
        )
        visitadas = 0
        while habilitadas:
            nombre = habilitadas.popleft()
            visitadas += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    habilitadas.append(dependiente)
        if visitadas != len(grafo):
            raise ValueError("Las dependencias no pueden contener ciclos.")

        self._dependencias = grafo
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._en_curso = 0
        self._estados = {nombre: "pendiente" for nombre in sorted(grafo)}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - self._en_curso
        if libres == 0:
            return []

        seleccionadas = []
        for nombre, estado in self._estados.items():
            if estado == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                seleccionadas.append(nombre)
                if len(seleccionadas) == libres:
                    break

        for nombre in seleccionadas:
            self._estados[nombre] = "en_curso"
        self._en_curso += len(seleccionadas)
        return seleccionadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano.")
        if (
            not isinstance(nombre, str)
            or not nombre
            or self._estados.get(nombre) != "en_curso"
        ):
            raise ValueError("La tarea debe existir y estar en curso.")

        bloqueadas = set()
        if not exito:
            pendientes = list(self._dependientes[nombre])
            while pendientes:
                dependiente = pendientes.pop()
                if (
                    self._estados[dependiente] == "pendiente"
                    and dependiente not in bloqueadas
                ):
                    bloqueadas.add(dependiente)
                    pendientes.extend(self._dependientes[dependiente])

        self._estados[nombre] = "listo" if exito else "fallo"
        for bloqueada in bloqueadas:
            self._estados[bloqueada] = "bloqueado"
        self._en_curso -= 1

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
