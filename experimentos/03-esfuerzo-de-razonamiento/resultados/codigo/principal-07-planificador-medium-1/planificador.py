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

        for nombre in dependencias:
            if not isinstance(nombre, str) or not nombre:
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
            grafo[nombre] = copia

        dependientes = {nombre: set() for nombre in grafo}
        restantes = {nombre: len(requisitos) for nombre, requisitos in grafo.items()}
        for nombre, requisitos in grafo.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = [nombre for nombre in grafo if restantes[nombre] == 0]
        visitados = 0
        while disponibles:
            nombre = disponibles.pop()
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
        self._estados = {nombre: "pendiente" for nombre in grafo}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in sorted(self._estados):
            if libres == 0:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                self._estados[nombre] = "en_curso"
                nuevas.append(nombre)
                libres -= 1
        return nuevas

    def completar(self, nombre, exito=True):
        if (
            not isinstance(nombre, str)
            or self._estados.get(nombre) != "en_curso"
            or not isinstance(exito, bool)
        ):
            raise ValueError("Se requiere una tarea en curso y un éxito booleano")

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
