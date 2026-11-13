class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        requisitos_por_tarea = {}
        for nombre, requisitos in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres de las tareas deben ser strings no vacíos")

            try:
                iterador = iter(requisitos)
            except TypeError as error:
                raise ValueError("los prerrequisitos deben ser iterables") from error

            requisitos_unicos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("los nombres de los prerrequisitos deben ser strings no vacíos")
                requisitos_unicos.add(requisito)
            requisitos_por_tarea[nombre] = requisitos_unicos

        nombres = set(requisitos_por_tarea)
        for requisitos in requisitos_por_tarea.values():
            if not requisitos.issubset(nombres):
                raise ValueError("hay un prerrequisito desconocido")

        dependientes = {nombre: set() for nombre in requisitos_por_tarea}
        grados_entrada = {}
        for nombre, requisitos in requisitos_por_tarea.items():
            grados_entrada[nombre] = len(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = [nombre for nombre, grado in grados_entrada.items() if grado == 0]
        procesadas = 0
        while disponibles:
            actual = disponibles.pop()
            procesadas += 1
            for dependiente in dependientes[actual]:
                grados_entrada[dependiente] -= 1
                if grados_entrada[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesadas != len(requisitos_por_tarea):
            raise ValueError("las dependencias contienen un ciclo")

        self._dependencias = requisitos_por_tarea
        self._dependientes = dependientes
        self._capacidad = int(capacidad)
        self._estados = {nombre: "pendiente" for nombre in requisitos_por_tarea}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        ocupados = sum(estado == "en_curso" for estado in self._estados.values())
        lugares_libres = self._capacidad - ocupados
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(self._estados[requisito] == "listo" for requisito in self._dependencias[nombre])
        )
        lanzadas = habilitadas[:lugares_libres]
        if lanzadas:
            nuevos_estados = self._estados.copy()
            for nombre in lanzadas:
                nuevos_estados[nombre] = "en_curso"
            self._estados = nuevos_estados
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser booleano")

        nuevos_estados = self._estados.copy()
        if exito:
            nuevos_estados[nombre] = "listo"
        else:
            nuevos_estados[nombre] = "fallo"
            por_revisar = list(self._dependientes[nombre])
            visitados = set()
            while por_revisar:
                dependiente = por_revisar.pop()
                if dependiente in visitados:
                    continue
                visitados.add(dependiente)
                if nuevos_estados[dependiente] == "pendiente":
                    nuevos_estados[dependiente] = "bloqueado"
                por_revisar.extend(self._dependientes[dependiente])
        self._estados = nuevos_estados

    def terminado(self):
        return all(estado in ("listo", "fallo", "bloqueado") for estado in self._estados.values())
