from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")

        entrada = dict(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in entrada):
            raise ValueError("Los nombres deben ser strings no vacíos")

        grafo = {}
        sucesores = {nombre: set() for nombre in entrada}
        for nombre, requisitos in entrada.items():
            try:
                requisitos = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            copia = set()
            for requisito in requisitos:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in entrada:
                    raise ValueError("Prerrequisito desconocido")
                copia.add(requisito)
            grafo[nombre] = copia
            for requisito in copia:
                sucesores[requisito].add(nombre)

        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        habilitados = deque(nombre for nombre, cantidad in restantes.items() if cantidad == 0)
        visitados = 0
        while habilitados:
            nombre = habilitados.popleft()
            visitados += 1
            for sucesor in sucesores[nombre]:
                restantes[sucesor] -= 1
                if restantes[sucesor] == 0:
                    habilitados.append(sucesor)
        if visitados != len(grafo):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = grafo
        self._sucesores = sucesores
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in grafo}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in sorted(self._estados):
            if len(nuevas) >= libres:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                nuevas.append(nombre)
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
            raise ValueError("La tarea debe estar en curso y exito debe ser bool")
        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            pendientes = deque(self._sucesores[nombre])
            while pendientes:
                sucesor = pendientes.popleft()
                if self._estados[sucesor] == "pendiente":
                    self._estados[sucesor] = "bloqueado"
                    pendientes.extend(self._sucesores[sucesor])

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
