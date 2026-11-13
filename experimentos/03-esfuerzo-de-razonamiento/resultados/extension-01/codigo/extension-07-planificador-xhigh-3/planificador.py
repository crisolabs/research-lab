from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")
        if any(not isinstance(nombre, str) or not nombre for nombre in dependencias):
            raise ValueError("Los nombres deben ser strings no vacíos")

        grafo = {}
        for nombre, requisitos in dependencias.items():
            try:
                iterador = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error

            copia = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in dependencias:
                    raise ValueError("Todos los prerrequisitos deben existir")
                copia.add(requisito)
            grafo[nombre] = frozenset(copia)

        dependientes = {nombre: set() for nombre in grafo}
        grados = {}
        for nombre, requisitos in grafo.items():
            grados[nombre] = len(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = deque(nombre for nombre in grafo if grados[nombre] == 0)
        visitadas = 0
        while disponibles:
            nombre = disponibles.popleft()
            visitadas += 1
            for dependiente in dependientes[nombre]:
                grados[dependiente] -= 1
                if grados[dependiente] == 0:
                    disponibles.append(dependiente)
        if visitadas != len(grafo):
            raise ValueError("Las dependencias no pueden contener ciclos")

        orden = tuple(sorted(grafo))
        estados = {nombre: "pendiente" for nombre in orden}
        dependientes = {
            nombre: frozenset(nombres) for nombre, nombres in dependientes.items()
        }
        self._capacidad = capacidad
        self._dependencias = grafo
        self._dependientes = dependientes
        self._orden = orden
        self._estados = estados

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        if libres <= 0:
            return []

        nuevas = []
        for nombre in self._orden:
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                nuevas.append(nombre)
                if len(nuevas) == libres:
                    break

        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if (
            not isinstance(nombre, str)
            or nombre not in self._estados
            or self._estados[nombre] != "en_curso"
            or not isinstance(exito, bool)
        ):
            raise ValueError("Se requiere una tarea en curso y un éxito booleano")

        if exito:
            self._estados[nombre] = "listo"
            return None

        alcanzadas = {nombre}
        pendientes = [nombre]
        while pendientes:
            actual = pendientes.pop()
            for dependiente in self._dependientes[actual]:
                if dependiente not in alcanzadas:
                    alcanzadas.add(dependiente)
                    pendientes.append(dependiente)

        self._estados[nombre] = "fallo"
        for dependiente in alcanzadas:
            if self._estados[dependiente] == "pendiente":
                self._estados[dependiente] = "bloqueado"
        return None

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
