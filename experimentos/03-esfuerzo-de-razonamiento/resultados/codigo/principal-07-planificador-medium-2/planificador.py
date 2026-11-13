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

        requisitos = {}
        dependientes = {nombre: set() for nombre in entrada}
        for nombre, prerrequisitos in entrada.items():
            try:
                iterador = iter(prerrequisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            copia = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos")
                if requisito not in entrada:
                    raise ValueError("Prerrequisito desconocido")
                copia.add(requisito)
            requisitos[nombre] = copia
            for requisito in copia:
                dependientes[requisito].add(nombre)

        grados = {nombre: len(prerrequisitos) for nombre, prerrequisitos in requisitos.items()}
        disponibles = deque(nombre for nombre, grado in grados.items() if grado == 0)
        visitados = 0
        while disponibles:
            nombre = disponibles.popleft()
            visitados += 1
            for dependiente in dependientes[nombre]:
                grados[dependiente] -= 1
                if grados[dependiente] == 0:
                    disponibles.append(dependiente)
        if visitados != len(requisitos):
            raise ValueError("Las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._requisitos = requisitos
        self._dependientes = dependientes
        self._orden = sorted(requisitos)
        self._estados = {nombre: "pendiente" for nombre in requisitos}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        lanzadas = []
        for nombre in self._orden:
            if libres == 0:
                break
            if self._estados[nombre] == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._requisitos[nombre]
            ):
                self._estados[nombre] = "en_curso"
                lanzadas.append(nombre)
                libres -= 1
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("El éxito debe ser bool")
        if not isinstance(nombre, str) or self._estados.get(nombre) != "en_curso":
            raise ValueError("La tarea debe existir y estar en curso")

        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            pendientes = deque([nombre])
            while pendientes:
                actual = pendientes.popleft()
                for dependiente in self._dependientes[actual]:
                    if self._estados[dependiente] == "pendiente":
                        self._estados[dependiente] = "bloqueado"
                        pendientes.append(dependiente)

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
