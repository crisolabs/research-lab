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

        nombres = tuple(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("Los nombres deben ser strings no vacíos")

        requisitos = {}
        for nombre in nombres:
            unicos = set()
            try:
                for requisito in dependencias[nombre]:
                    if not isinstance(requisito, str) or not requisito:
                        raise ValueError("Nombre de prerrequisito inválido")
                    if requisito not in dependencias:
                        raise ValueError("Prerrequisito desconocido")
                    unicos.add(requisito)
            except TypeError as exc:
                raise ValueError("Los prerrequisitos deben ser iterables") from exc
            requisitos[nombre] = frozenset(unicos)

        dependientes = {nombre: set() for nombre in nombres}
        restantes = {nombre: len(requisitos[nombre]) for nombre in nombres}
        for nombre, previos in requisitos.items():
            for previo in previos:
                dependientes[previo].add(nombre)

        disponibles = [nombre for nombre in nombres if restantes[nombre] == 0]
        visitados = 0
        while disponibles:
            nombre = disponibles.pop()
            visitados += 1
            for siguiente in dependientes[nombre]:
                restantes[siguiente] -= 1
                if restantes[siguiente] == 0:
                    disponibles.append(siguiente)
        if visitados != len(nombres):
            raise ValueError("Las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._requisitos = requisitos
        self._dependientes = dependientes
        self._estados = {nombre: "pendiente" for nombre in nombres}

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
                self._estados[previo] == "listo"
                for previo in self._requisitos[nombre]
            ):
                nuevas.append(nombre)
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if (
            not isinstance(nombre, str)
            or self._estados.get(nombre) != "en_curso"
            or not isinstance(exito, bool)
        ):
            raise ValueError("La tarea debe estar en curso y exito debe ser bool")

        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            pendientes = [nombre]
            while pendientes:
                actual = pendientes.pop()
                for siguiente in self._dependientes[actual]:
                    if self._estados[siguiente] == "pendiente":
                        self._estados[siguiente] = "bloqueado"
                        pendientes.append(siguiente)

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
