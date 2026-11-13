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

        requisitos = {}
        for nombre, entradas in dependencias.items():
            try:
                iterador = iter(entradas)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error

            unicos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in dependencias:
                    raise ValueError("Todos los prerrequisitos deben existir")
                unicos.add(requisito)
            requisitos[nombre] = frozenset(unicos)

        dependientes = {nombre: set() for nombre in requisitos}
        restantes = {}
        for nombre, previos in requisitos.items():
            restantes[nombre] = len(previos)
            for previo in previos:
                dependientes[previo].add(nombre)

        habilitados = [nombre for nombre, cantidad in restantes.items() if cantidad == 0]
        visitados = 0
        while habilitados:
            nombre = habilitados.pop()
            visitados += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    habilitados.append(dependiente)
        if visitados != len(requisitos):
            raise ValueError("Las dependencias no pueden contener ciclos")

        self._capacidad = capacidad
        self._dependencias = requisitos
        self._dependientes = {
            nombre: frozenset(siguientes)
            for nombre, siguientes in dependientes.items()
        }
        self._orden = tuple(sorted(requisitos))
        self._estados = dict.fromkeys(requisitos, "pendiente")

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in self._orden:
            if len(nuevas) == libres:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[previo] == "listo"
                for previo in self._dependencias[nombre]
            ):
                nuevas.append(nombre)
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("La tarea debe existir")
        if self._estados[nombre] != "en_curso":
            raise ValueError("La tarea debe estar en curso")
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano")

        if exito:
            self._estados[nombre] = "listo"
            return None

        bloqueadas = set()
        pendientes = list(self._dependientes[nombre])
        while pendientes:
            dependiente = pendientes.pop()
            if dependiente not in bloqueadas and self._estados[dependiente] == "pendiente":
                bloqueadas.add(dependiente)
                pendientes.extend(self._dependientes[dependiente])

        self._estados[nombre] = "fallo"
        for dependiente in bloqueadas:
            self._estados[dependiente] = "bloqueado"
        return None

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
