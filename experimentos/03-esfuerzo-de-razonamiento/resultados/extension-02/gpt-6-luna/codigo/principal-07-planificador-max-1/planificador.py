class Planificador:
    _ESTADOS_TERMINALES = frozenset(("listo", "fallo", "bloqueado"))

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        nombres = list(dependencias.keys())
        for nombre in nombres:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres de las tareas deben ser strings no vacíos")

        conjunto_nombres = set(nombres)
        prerequisitos = {}
        dependientes = {nombre: set() for nombre in nombres}

        for nombre in nombres:
            try:
                iterador = iter(dependencias[nombre])
            except TypeError as exc:
                raise ValueError("los prerrequisitos deben ser iterables") from exc

            requisitos = set()
            try:
                for requisito in iterador:
                    if not isinstance(requisito, str) or not requisito:
                        raise ValueError(
                            "los nombres de los prerrequisitos deben ser strings no vacíos"
                        )
                    if requisito not in conjunto_nombres:
                        raise ValueError("prerrequisito desconocido")
                    requisitos.add(requisito)
            except ValueError:
                raise

            prerequisitos[nombre] = frozenset(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        pendientes_por_resolver = {
            nombre: len(requisitos) for nombre, requisitos in prerequisitos.items()
        }
        listos = [nombre for nombre, cuenta in pendientes_por_resolver.items() if cuenta == 0]
        resueltos = 0
        while listos:
            nombre = listos.pop()
            resueltos += 1
            for dependiente in dependientes[nombre]:
                pendientes_por_resolver[dependiente] -= 1
                if pendientes_por_resolver[dependiente] == 0:
                    listos.append(dependiente)
        if resueltos != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._prerequisitos = prerequisitos
        self._dependientes = {
            nombre: frozenset(tareas) for nombre, tareas in dependientes.items()
        }
        self._estados = {nombre: "pendiente" for nombre in nombres}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        en_curso = sum(estado == "en_curso" for estado in self._estados.values())
        lugares_libres = self._capacidad - en_curso
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(
                self._estados[requisito] == "listo"
                for requisito in self._prerequisitos[nombre]
            )
        )
        nuevas = habilitadas[:lugares_libres]
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")

        if exito:
            self._estados[nombre] = "listo"
            return None

        self._estados[nombre] = "fallo"
        por_visitar = list(self._dependientes[nombre])
        visitados = set()
        while por_visitar:
            tarea = por_visitar.pop()
            if tarea in visitados:
                continue
            visitados.add(tarea)
            if self._estados[tarea] == "pendiente":
                self._estados[tarea] = "bloqueado"
            por_visitar.extend(self._dependientes[tarea])
        return None

    def terminado(self):
        return all(estado in self._ESTADOS_TERMINALES for estado in self._estados.values())
