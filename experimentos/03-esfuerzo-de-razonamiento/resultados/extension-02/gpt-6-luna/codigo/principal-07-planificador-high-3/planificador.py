"""Planificador de tareas con dependencias."""


class Planificador:
    """Administra el estado de un conjunto de tareas dependientes."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        nombres = list(dependencias.keys())
        for nombre in nombres:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres de tareas deben ser strings no vacíos")

        conjunto_nombres = set(nombres)
        requisitos = {}
        dependientes = {nombre: set() for nombre in nombres}
        for nombre, prerequisitos in dependencias.items():
            try:
                iterador = iter(prerequisitos)
            except TypeError as error:
                raise ValueError("cada conjunto de prerrequisitos debe ser iterable") from error

            unicos = set()
            for prerequisito in iterador:
                if not isinstance(prerequisito, str) or not prerequisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                if prerequisito not in conjunto_nombres:
                    raise ValueError("prerrequisito desconocido")
                unicos.add(prerequisito)
            requisitos[nombre] = unicos
            for prerequisito in unicos:
                dependientes[prerequisito].add(nombre)

        # Kahn permite detectar ciclos sin depender del límite de recursión.
        pendientes = {nombre: len(requisitos[nombre]) for nombre in nombres}
        disponibles = [nombre for nombre, cantidad in pendientes.items() if cantidad == 0]
        procesados = 0
        while disponibles:
            nombre = disponibles.pop()
            procesados += 1
            for dependiente in dependientes[nombre]:
                pendientes[dependiente] -= 1
                if pendientes[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesados != len(nombres):
            raise ValueError("el grafo de dependencias contiene un ciclo")

        self._requisitos = requisitos
        self._dependientes = dependientes
        self._estados = {nombre: "pendiente" for nombre in nombres}
        self._capacidad = capacidad

    def estados(self):
        """Devuelve una copia de los estados actuales."""
        return self._estados.copy()

    def tomar(self):
        """Lanza en orden lexicográfico las tareas habilitadas disponibles."""
        en_curso = sum(estado == "en_curso" for estado in self._estados.values())
        lugares_libres = self._capacidad - en_curso
        if lugares_libres <= 0:
            return []

        nuevas = []
        for nombre in sorted(self._estados):
            if self._estados[nombre] != "pendiente":
                continue
            if all(self._estados[prerequisito] == "listo"
                   for prerequisito in self._requisitos[nombre]):
                nuevas.append(nombre)
                if len(nuevas) == lugares_libres:
                    break

        for nombre in nuevas:
            self._estados[nombre] = "en_curso"
        return nuevas

    def completar(self, nombre, exito=True):
        """Completa una tarea en curso y propaga bloqueos si falla."""
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = "listo"
            return None

        self._estados[nombre] = "fallo"
        por_visitar = list(self._dependientes[nombre])
        visitados = set()
        while por_visitar:
            dependiente = por_visitar.pop()
            if dependiente in visitados:
                continue
            visitados.add(dependiente)
            if self._estados[dependiente] == "pendiente":
                self._estados[dependiente] = "bloqueado"
            por_visitar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        """Indica si todas las tareas alcanzaron un estado final."""
        return all(estado in {"listo", "fallo", "bloqueado"}
                   for estado in self._estados.values())
