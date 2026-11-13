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
                    raise ValueError("Prerrequisito desconocido")
                copia.add(requisito)
            grafo[nombre] = frozenset(copia)

        dependientes = {nombre: set() for nombre in grafo}
        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        for nombre, requisitos in grafo.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        habilitadas = [nombre for nombre, cantidad in restantes.items() if cantidad == 0]
        visitadas = 0
        while habilitadas:
            nombre = habilitadas.pop()
            visitadas += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    habilitadas.append(dependiente)
        if visitadas != len(grafo):
            raise ValueError("El grafo contiene ciclos")

        self._dependencias = grafo
        self._dependientes = {
            nombre: frozenset(tareas) for nombre, tareas in dependientes.items()
        }
        self._orden = tuple(sorted(grafo))
        self._capacidad = capacidad
        self._estados = dict.fromkeys(grafo, "pendiente")

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in self._orden:
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
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("Tarea desconocida")
        if self._estados[nombre] != "en_curso":
            raise ValueError("La tarea debe estar en curso")

        if exito:
            self._estados[nombre] = "listo"
            return None

        por_visitar = list(self._dependientes[nombre])
        visitadas = set()
        bloqueadas = []
        while por_visitar:
            dependiente = por_visitar.pop()
            if dependiente in visitadas:
                continue
            visitadas.add(dependiente)
            if self._estados[dependiente] == "pendiente":
                bloqueadas.append(dependiente)
            por_visitar.extend(self._dependientes[dependiente])

        self._estados[nombre] = "fallo"
        for dependiente in bloqueadas:
            self._estados[dependiente] = "bloqueado"
        return None

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
