from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        copia = {}
        for nombre, prerrequisitos in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres de tarea deben ser strings no vacíos")

            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError("los prerrequisitos deben ser iterables") from None

            requisitos = set()
            for prerrequisito in iterador:
                if not isinstance(prerrequisito, str) or not prerrequisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                requisitos.add(prerrequisito)
            copia[nombre] = frozenset(requisitos)

        for requisitos in copia.values():
            if any(requisito not in copia for requisito in requisitos):
                raise ValueError("hay una referencia a una tarea desconocida")

        dependientes = {nombre: set() for nombre in copia}
        pendientes = {}
        for nombre, requisitos in copia.items():
            pendientes[nombre] = len(requisitos)
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        listos = deque(nombre for nombre, cantidad in pendientes.items() if cantidad == 0)
        visitados = 0
        while listos:
            nombre = listos.popleft()
            visitados += 1
            for dependiente in dependientes[nombre]:
                pendientes[dependiente] -= 1
                if pendientes[dependiente] == 0:
                    listos.append(dependiente)
        if visitados != len(copia):
            raise ValueError("el grafo de dependencias contiene un ciclo")

        self._dependencias = copia
        self._dependientes = {
            nombre: frozenset(tareas) for nombre, tareas in dependientes.items()
        }
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in copia}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        lugares_libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        if lugares_libres <= 0:
            return []

        nuevas = []
        for nombre in sorted(self._dependencias):
            if lugares_libres == 0:
                break
            if self._estados[nombre] != "pendiente":
                continue
            if all(self._estados[requisito] == "listo"
                   for requisito in self._dependencias[nombre]):
                self._estados[nombre] = "en_curso"
                nuevas.append(nombre)
                lugares_libres -= 1
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or not nombre:
            raise ValueError("nombre debe ser un string no vacío")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if nombre not in self._estados or self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")

        if exito:
            self._estados[nombre] = "listo"
        else:
            self._estados[nombre] = "fallo"
            por_bloquear = list(self._dependientes[nombre])
            visitados = set()
            while por_bloquear:
                dependiente = por_bloquear.pop()
                if dependiente in visitados:
                    continue
                visitados.add(dependiente)
                if self._estados[dependiente] == "pendiente":
                    self._estados[dependiente] = "bloqueado"
                por_bloquear.extend(self._dependientes[dependiente])

        return None

    def terminado(self):
        return all(estado in {"listo", "fallo", "bloqueado"}
                   for estado in self._estados.values())
