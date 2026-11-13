from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")
        if any(not isinstance(nombre, str) or not nombre for nombre in dependencias):
            raise ValueError("Los nombres deben ser strings no vacíos")

        grafo = {}
        for nombre, requisitos in dependencias.items():
            try:
                requisitos = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            copia = set()
            for requisito in requisitos:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los prerrequisitos deben ser nombres válidos")
                if requisito not in dependencias:
                    raise ValueError("Prerrequisito desconocido")
                copia.add(requisito)
            grafo[nombre] = frozenset(copia)

        dependientes = {nombre: set() for nombre in grafo}
        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        for nombre, requisitos in grafo.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = deque(nombre for nombre in grafo if restantes[nombre] == 0)
        visitados = 0
        while disponibles:
            nombre = disponibles.popleft()
            visitados += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    disponibles.append(dependiente)
        if visitados != len(grafo):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = grafo
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._nombres = tuple(sorted(grafo))
        self._estados = dict.fromkeys(grafo, "pendiente")

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in self._nombres:
            if libres == 0:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                nuevas.append(nombre)
                libres -= 1
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("El resultado debe ser booleano")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("Nombre desconocido")
        if self._estados[nombre] != "en_curso":
            raise ValueError("La tarea debe estar en curso")

        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            pendientes = [nombre]
            while pendientes:
                actual = pendientes.pop()
                for dependiente in self._dependientes[actual]:
                    if self._estados[dependiente] == "pendiente":
                        self._estados[dependiente] = "bloqueado"
                        pendientes.append(dependiente)

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
