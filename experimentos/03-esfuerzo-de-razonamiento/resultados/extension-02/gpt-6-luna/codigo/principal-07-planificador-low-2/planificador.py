"""Planificador sencillo de tareas con dependencias."""


class Planificador:
    """Administra el lanzamiento y la finalización de tareas."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        try:
            elementos = list(dependencias.items())
        except (AttributeError, TypeError):
            raise ValueError("dependencias debe ser un diccionario") from None

        grafo = {}
        for nombre, prerrequisitos in elementos:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres deben ser strings no vacíos")
            try:
                requisitos = list(prerrequisitos)
            except TypeError:
                raise ValueError("cada conjunto de prerrequisitos debe ser iterable") from None
            if any(not isinstance(req, str) or not req for req in requisitos):
                raise ValueError("los prerrequisitos deben ser strings no vacíos")
            grafo[nombre] = set(requisitos)

        for requisitos in grafo.values():
            if not requisitos.issubset(grafo):
                raise ValueError("referencia a un prerrequisito desconocido")

        # Una búsqueda en profundidad detecta ciclos, incluyendo auto-dependencias.
        colores = {}

        def visitar(nombre):
            color = colores.get(nombre, 0)
            if color == 1:
                raise ValueError("el grafo contiene un ciclo")
            if color == 2:
                return
            colores[nombre] = 1
            for req in grafo[nombre]:
                visitar(req)
            colores[nombre] = 2

        for nombre in grafo:
            visitar(nombre)

        self._dependencias = grafo
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in grafo}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        if libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(self._estados[req] == "listo" for req in self._dependencias[nombre])
        )
        lanzadas = habilitadas[:libres]
        for nombre in lanzadas:
            self._estados[nombre] = "en_curso"
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if nombre not in self._estados or self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")

        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            afectadas = {nombre}
            cambio = True
            while cambio:
                cambio = False
                for tarea, requisitos in self._dependencias.items():
                    if (
                        self._estados[tarea] == "pendiente"
                        and requisitos.intersection(afectadas)
                    ):
                        self._estados[tarea] = "bloqueado"
                        afectadas.add(tarea)
                        cambio = True
        return None

    def terminado(self):
        return all(
            estado in {"listo", "fallo", "bloqueado"}
            for estado in self._estados.values()
        )
