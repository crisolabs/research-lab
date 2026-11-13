"""Planificador de dependencias sin ejecución de tareas."""

class Planificador:
    """Administra el estado de un conjunto de tareas dependientes."""

    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    LISTO = "listo"
    FALLO = "fallo"
    BLOQUEADO = "bloqueado"

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        grafo = {}
        for nombre, prerrequisitos in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("nombre de tarea inválido")
            try:
                requisitos = set(prerrequisitos)
            except (TypeError, ValueError):
                raise ValueError("prerrequisitos inválidos") from None
            if any(not isinstance(req, str) or not req for req in requisitos):
                raise ValueError("nombre de prerrequisito inválido")
            grafo[nombre] = requisitos

        for requisitos in grafo.values():
            if not requisitos.issubset(grafo):
                raise ValueError("prerrequisito desconocido")

        # DFS con colores para rechazar cualquier ciclo, incluido el propio.
        colores = {}
        def visitar(nombre):
            color = colores.get(nombre, 0)
            if color == 1:
                raise ValueError("el grafo contiene un ciclo")
            if color == 2:
                return
            colores[nombre] = 1
            for requisito in grafo[nombre]:
                visitar(requisito)
            colores[nombre] = 2

        for nombre in grafo:
            visitar(nombre)

        self._dependencias = {nombre: frozenset(reqs) for nombre, reqs in grafo.items()}
        self._capacidad = capacidad
        self._estados = {nombre: self.PENDIENTE for nombre in grafo}

    def estados(self):
        """Devuelve una copia independiente de los estados actuales."""
        return self._estados.copy()

    def tomar(self):
        """Inicia tareas disponibles, en orden lexicográfico."""
        libres = self._capacidad - sum(estado == self.EN_CURSO for estado in self._estados.values())
        if libres <= 0:
            return []
        disponibles = sorted(
            nombre for nombre, estado in self._estados.items()
            if estado == self.PENDIENTE
            and all(self._estados[req] == self.LISTO for req in self._dependencias[nombre])
        )[:libres]
        for nombre in disponibles:
            self._estados[nombre] = self.EN_CURSO
        return disponibles

    def completar(self, nombre, exito=True):
        """Completa una tarea activa y propaga fallos a sus dependientes."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if (not isinstance(nombre, str) or nombre not in self._estados
                or self._estados[nombre] != self.EN_CURSO):
            raise ValueError("la tarea no está en curso")

        self._estados[nombre] = self.LISTO if exito else self.FALLO
        if not exito:
            # Propaga el bloqueo por dependencias, sin afectar tareas independientes.
            bloqueados = {nombre}
            cambio = True
            while cambio:
                cambio = False
                for tarea, estado in self._estados.items():
                    if (estado == self.PENDIENTE and
                            self._dependencias[tarea].intersection(bloqueados)):
                        self._estados[tarea] = self.BLOQUEADO
                        bloqueados.add(tarea)
                        cambio = True

    def terminado(self):
        """Indica si no quedan tareas pendientes o en curso."""
        return all(estado in (self.LISTO, self.FALLO, self.BLOQUEADO)
                   for estado in self._estados.values())
