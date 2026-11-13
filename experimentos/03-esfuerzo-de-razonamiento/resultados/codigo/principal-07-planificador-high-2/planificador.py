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
            copia = set()
            try:
                iterador = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            for requisito in iterador:
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
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = grafo
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in grafo}
        self._orden = sorted(grafo)
        self._en_curso = 0

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        lanzadas = []
        for nombre in self._orden:
            if self._en_curso == self._capacidad:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                self._estados[nombre] = "en_curso"
                self._en_curso += 1
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("Nombre desconocido")
        if self._estados[nombre] != "en_curso":
            raise ValueError("La tarea debe estar en curso")

        self._estados[nombre] = "listo" if exito else "fallo"
        self._en_curso -= 1
        if not exito:
            pendientes = list(self._dependientes[nombre])
            while pendientes:
                dependiente = pendientes.pop()
                if self._estados[dependiente] == "pendiente":
                    self._estados[dependiente] = "bloqueado"
                    pendientes.extend(self._dependientes[dependiente])

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
