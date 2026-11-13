"""Planificador sencillo de tareas con dependencias."""


class Planificador:
    """Administra estados de tareas sin ejecutar su trabajo."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        try:
            elementos = list(dependencias.items())
        except (AttributeError, TypeError):
            raise ValueError("dependencias debe ser un diccionario") from None

        copia = {}
        for nombre, prerrequisitos in elementos:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres deben ser strings no vacíos")
            try:
                prereqs = list(prerrequisitos)
            except TypeError:
                raise ValueError("los prerrequisitos deben ser iterables") from None
            if any(not isinstance(prereq, str) or not prereq for prereq in prereqs):
                raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
            copia[nombre] = set(prereqs)

        for prereqs in copia.values():
            if not prereqs.issubset(copia):
                raise ValueError("referencia a un prerrequisito desconocido")

        # Un recorrido de tres colores rechaza tanto ciclos como auto dependencias.
        colores = {nombre: 0 for nombre in copia}

        def visitar(nombre):
            if colores[nombre] == 1:
                raise ValueError("el grafo contiene un ciclo")
            if colores[nombre] == 2:
                return
            colores[nombre] = 1
            for prereq in copia[nombre]:
                visitar(prereq)
            colores[nombre] = 2

        for nombre in copia:
            visitar(nombre)

        self._dependencias = copia
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in copia}

    def estados(self):
        """Devuelve una copia de los estados actuales."""
        return self._estados.copy()

    def tomar(self):
        """Lanza tareas habilitadas hasta completar la capacidad disponible."""
        ocupados = sum(estado == "en_curso" for estado in self._estados.values())
        libres = self._capacidad - ocupados
        if libres <= 0:
            return []

        nuevas = []
        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == "pendiente"
            and all(self._estados[prereq] == "listo" for prereq in self._dependencias[nombre])
        )
        for nombre in habilitadas[:libres]:
            self._estados[nombre] = "en_curso"
            nuevas.append(nombre)
        return nuevas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea que está en curso."""
        if nombre not in self._estados or self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = "listo"
            return None

        self._estados[nombre] = "fallo"
        bloqueados = {nombre}
        cambio = True
        while cambio:
            cambio = False
            for tarea, prereqs in self._dependencias.items():
                if (
                    self._estados[tarea] == "pendiente"
                    and any(prereq in bloqueados for prereq in prereqs)
                ):
                    self._estados[tarea] = "bloqueado"
                    bloqueados.add(tarea)
                    cambio = True
        return None

    def terminado(self):
        """Indica si todas las tareas alcanzaron un estado final."""
        return all(estado in {"listo", "fallo", "bloqueado"} for estado in self._estados.values())
