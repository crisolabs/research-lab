"""Planificador de tareas con dependencias y capacidad limitada."""


class Planificador:
    """Administra el estado de un grafo de tareas sin ejecutarlas."""

    __slots__ = ("_capacidad", "_prerrequisitos", "_dependientes", "_estados")

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        tareas = {}
        for nombre, requisitos in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres de tareas deben ser strings no vacíos")
            try:
                iterador = iter(requisitos)
            except TypeError as exc:
                raise ValueError("los prerrequisitos deben ser iterables") from exc

            nombres_requisitos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                nombres_requisitos.add(requisito)
            tareas[nombre] = frozenset(nombres_requisitos)

        for nombre, requisitos in tareas.items():
            if any(requisito not in tareas for requisito in requisitos):
                raise ValueError("hay una referencia a una tarea desconocida")

        dependientes_mutables = {nombre: set() for nombre in tareas}
        grados = {nombre: len(requisitos) for nombre, requisitos in tareas.items()}
        for nombre, requisitos in tareas.items():
            for requisito in requisitos:
                dependientes_mutables[requisito].add(nombre)

        disponibles = [nombre for nombre, grado in grados.items() if grado == 0]
        procesadas = 0
        while disponibles:
            nombre = disponibles.pop()
            procesadas += 1
            for dependiente in dependientes_mutables[nombre]:
                grados[dependiente] -= 1
                if grados[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesadas != len(tareas):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._prerrequisitos = tareas
        self._dependientes = {
            nombre: frozenset(dependientes)
            for nombre, dependientes in dependientes_mutables.items()
        }
        self._estados = {nombre: "pendiente" for nombre in tareas}

    def estados(self):
        """Devuelve una copia del mapa de estados actual."""
        return self._estados.copy()

    def tomar(self):
        """Lanza las tareas habilitadas hasta alcanzar la capacidad."""
        en_curso = sum(estado == "en_curso" for estado in self._estados.values())
        lugares_libres = self._capacidad - en_curso
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(self._estados[requisito] == "listo"
                    for requisito in self._prerrequisitos[nombre])
        )
        nuevas = habilitadas[:lugares_libres]
        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        """Completa una tarea en curso y propaga sus fallas."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or self._estados.get(nombre) != "en_curso":
            raise ValueError("la tarea debe existir y estar en curso")

        nuevo_estado = "listo" if exito else "fallo"
        bloqueadas = []
        if not exito:
            visitadas = {nombre}
            por_visitar = list(self._dependientes[nombre])
            while por_visitar:
                dependiente = por_visitar.pop()
                if dependiente in visitadas:
                    continue
                visitadas.add(dependiente)
                if self._estados[dependiente] == "pendiente":
                    bloqueadas.append(dependiente)
                por_visitar.extend(self._dependientes[dependiente])

        self._estados[nombre] = nuevo_estado
        for dependiente in bloqueadas:
            self._estados[dependiente] = "bloqueado"

    def terminado(self):
        """Indica si todas las tareas llegaron a un estado terminal."""
        return all(
            estado in {"listo", "fallo", "bloqueado"}
            for estado in self._estados.values()
        )
