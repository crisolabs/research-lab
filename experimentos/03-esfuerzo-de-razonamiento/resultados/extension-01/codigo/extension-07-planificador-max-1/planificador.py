class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("La capacidad debe ser un entero positivo.")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario.")

        nombres = tuple(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("Los nombres deben ser strings no vacíos.")
        conocidos = set(nombres)
        copia = {}
        dependientes = {nombre: set() for nombre in nombres}
        for nombre, prerrequisitos in dependencias.items():
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError("Los prerrequisitos deben ser iterables.") from None
            requisitos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("Los nombres deben ser strings no vacíos.")
                if requisito not in conocidos:
                    raise ValueError("Todos los prerrequisitos deben existir.")
                requisitos.add(requisito)
            copia[nombre] = frozenset(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        restantes = {nombre: len(requisitos) for nombre, requisitos in copia.items()}
        disponibles = [nombre for nombre in nombres if restantes[nombre] == 0]
        procesadas = 0
        while disponibles:
            nombre = disponibles.pop()
            procesadas += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesadas != len(nombres):
            raise ValueError("Las dependencias no pueden contener ciclos.")

        self._dependencias = copia
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = dict.fromkeys(sorted(nombres), "pendiente")

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre, estado in self._estados.items():
            if libres == 0:
                break
            if estado == "pendiente" and all(
                self._estados[requisito] == "listo"
                for requisito in self._dependencias[nombre]
            ):
                nuevas.append(nombre)
                libres -= 1
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if (
            not isinstance(exito, bool)
            or not isinstance(nombre, str)
            or self._estados.get(nombre) != "en_curso"
        ):
            raise ValueError("Se requiere una tarea en curso y un éxito booleano.")
        if exito:
            self._estados[nombre] = "listo"
            return None

        afectadas = set()
        por_visitar = list(self._dependientes[nombre])
        while por_visitar:
            dependiente = por_visitar.pop()
            if dependiente in afectadas:
                continue
            afectadas.add(dependiente)
            por_visitar.extend(self._dependientes[dependiente])

        self._estados[nombre] = "fallo"
        for dependiente in afectadas:
            if self._estados[dependiente] == "pendiente":
                self._estados[dependiente] = "bloqueado"
        return None

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
