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

        nombres = tuple(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("Los nombres deben ser strings no vacíos")

        copia = {}
        for nombre in nombres:
            try:
                requisitos = iter(dependencias[nombre])
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            unicos = set()
            for requisito in requisitos:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los prerrequisitos deben tener nombres válidos")
                if requisito not in dependencias:
                    raise ValueError("Prerrequisito desconocido")
                unicos.add(requisito)
            copia[nombre] = frozenset(unicos)

        dependientes = {nombre: set() for nombre in nombres}
        restantes = {nombre: len(copia[nombre]) for nombre in nombres}
        for nombre, requisitos in copia.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        habilitadas = deque(nombre for nombre in nombres if restantes[nombre] == 0)
        visitadas = 0
        while habilitadas:
            nombre = habilitadas.popleft()
            visitadas += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    habilitadas.append(dependiente)
        if visitadas != len(nombres):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = copia
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._orden = tuple(sorted(nombres))
        self._estados = {nombre: "pendiente" for nombre in nombres}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre in self._orden:
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
            or nombre not in self._estados
            or self._estados[nombre] != "en_curso"
            or not isinstance(exito, bool)
        ):
            raise ValueError("Se requiere una tarea en curso y un éxito booleano")

        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            bloqueadas = deque([nombre])
            while bloqueadas:
                actual = bloqueadas.popleft()
                for dependiente in self._dependientes[actual]:
                    if self._estados[dependiente] == "pendiente":
                        self._estados[dependiente] = "bloqueado"
                        bloqueadas.append(dependiente)

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
