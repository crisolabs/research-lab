from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or capacidad <= 0
        ):
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")

        entrada = dict(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in entrada):
            raise ValueError("Los nombres deben ser strings no vacíos")

        grafo = {}
        sucesoras = {nombre: set() for nombre in entrada}
        for nombre, requisitos in entrada.items():
            try:
                iterador = iter(requisitos)
            except TypeError:
                raise ValueError("Los prerrequisitos deben ser iterables") from None

            unicos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in entrada:
                    raise ValueError("Prerrequisito desconocido")
                unicos.add(requisito)
            grafo[nombre] = frozenset(unicos)
            for requisito in unicos:
                sucesoras[requisito].add(nombre)

        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        habilitadas = deque(nombre for nombre in grafo if restantes[nombre] == 0)
        visitadas = 0
        while habilitadas:
            nombre = habilitadas.popleft()
            visitadas += 1
            for sucesora in sucesoras[nombre]:
                restantes[sucesora] -= 1
                if restantes[sucesora] == 0:
                    habilitadas.append(sucesora)
        if visitadas != len(grafo):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = grafo
        self._sucesoras = sucesoras
        self._nombres = sorted(grafo)
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in grafo}
        self._en_curso = 0

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - self._en_curso
        nuevas = []
        if libres == 0:
            return nuevas

        for nombre in self._nombres:
            if self._estados[nombre] != "pendiente":
                continue
            if all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                self._estados[nombre] = "en_curso"
                self._en_curso += 1
                nuevas.append(nombre)
                if len(nuevas) == libres:
                    break
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano")
        if (
            not isinstance(nombre, str)
            or nombre not in self._estados
            or self._estados[nombre] != "en_curso"
        ):
            raise ValueError("La tarea debe existir y estar en curso")

        self._estados[nombre] = "listo" if exito else "fallo"
        self._en_curso -= 1
        if not exito:
            por_bloquear = deque([nombre])
            while por_bloquear:
                actual = por_bloquear.popleft()
                for sucesora in self._sucesoras[actual]:
                    if self._estados[sucesora] == "pendiente":
                        self._estados[sucesora] = "bloqueado"
                        por_bloquear.append(sucesora)

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
