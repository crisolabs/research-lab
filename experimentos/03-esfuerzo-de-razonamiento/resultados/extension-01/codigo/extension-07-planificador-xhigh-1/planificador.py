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

        entrada = dependencias.copy()
        if any(not isinstance(nombre, str) or not nombre for nombre in entrada):
            raise ValueError("Los nombres deben ser strings no vacíos")

        grafo = {}
        dependientes = {nombre: set() for nombre in entrada}
        for nombre, requisitos in entrada.items():
            try:
                requisitos = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error

            unicos = set()
            for requisito in requisitos:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in entrada:
                    raise ValueError("Todos los prerrequisitos deben existir")
                unicos.add(requisito)
            grafo[nombre] = frozenset(unicos)
            for requisito in unicos:
                dependientes[requisito].add(nombre)

        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        disponibles = [nombre for nombre, cantidad in restantes.items() if cantidad == 0]
        visitados = 0
        while disponibles:
            nombre = disponibles.pop()
            visitados += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    disponibles.append(dependiente)
        if visitados != len(grafo):
            raise ValueError("Las dependencias no pueden contener ciclos")

        self._capacidad = capacidad
        self._dependencias = grafo
        self._dependientes = dependientes
        self._nombres = tuple(sorted(grafo))
        self._estados = {nombre: "pendiente" for nombre in self._nombres}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        if libres <= 0:
            return nuevas
        for nombre in self._nombres:
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
        for dependiente in bloqueadas:
            self._estados[dependiente] = "bloqueado"

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
