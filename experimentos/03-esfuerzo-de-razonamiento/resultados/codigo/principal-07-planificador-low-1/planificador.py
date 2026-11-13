class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")

        nombres = set(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("Los nombres deben ser strings no vacíos")

        copia = {}
        for nombre, requisitos in dependencias.items():
            try:
                iterador = iter(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            unicos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los prerrequisitos deben ser nombres válidos")
                if requisito not in nombres:
                    raise ValueError("Prerrequisito desconocido")
                unicos.add(requisito)
            copia[nombre] = frozenset(unicos)

        dependientes = {nombre: set() for nombre in nombres}
        restantes = {nombre: len(requisitos) for nombre, requisitos in copia.items()}
        for nombre, requisitos in copia.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = [nombre for nombre in nombres if restantes[nombre] == 0]
        visitados = 0
        while disponibles:
            nombre = disponibles.pop()
            visitados += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    disponibles.append(dependiente)
        if visitados != len(nombres):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = copia
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in copia}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        lanzadas = []
        for nombre in sorted(self._estados):
            if len(lanzadas) == libres:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                self._estados[nombre] = "en_curso"
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("Tarea desconocida")
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser booleano")
        if self._estados[nombre] != "en_curso":
            raise ValueError("La tarea no está en curso")

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
