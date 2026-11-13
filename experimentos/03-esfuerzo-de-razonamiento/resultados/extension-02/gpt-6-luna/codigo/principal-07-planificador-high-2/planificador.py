"""Planificador de dependencias con capacidad limitada."""


class Planificador:
    """Administra el estado de un conjunto de tareas y sus prerrequisitos."""

    _PENDIENTE = "pendiente"
    _EN_CURSO = "en_curso"
    _LISTO = "listo"
    _FALLO = "fallo"
    _BLOQUEADO = "bloqueado"

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        grafo = {}
        for nombre, prerrequisitos in dependencias.items():
            if not self._nombre_valido(nombre):
                raise ValueError("los nombres de tarea deben ser strings no vacíos")
            if isinstance(prerrequisitos, (str, bytes)):
                raise ValueError("los prerrequisitos deben ser un iterable de nombres")
            try:
                iterador = iter(prerrequisitos)
            except TypeError as exc:
                raise ValueError("los prerrequisitos deben ser iterables") from exc

            unicos = set()
            for prerrequisito in iterador:
                if not self._nombre_valido(prerrequisito):
                    raise ValueError("los nombres de prerrequisito deben ser strings no vacíos")
                unicos.add(prerrequisito)
            grafo[nombre] = frozenset(unicos)

        for prerrequisitos in grafo.values():
            if not prerrequisitos.issubset(grafo):
                raise ValueError("hay prerrequisitos desconocidos")

        self._validar_aciclicidad(grafo)

        self._dependencias = grafo
        self._dependientes = {nombre: set() for nombre in grafo}
        for nombre, prerrequisitos in grafo.items():
            for prerrequisito in prerrequisitos:
                self._dependientes[prerrequisito].add(nombre)
        self._estados = {nombre: self._PENDIENTE for nombre in grafo}
        self._capacidad = capacidad

    @staticmethod
    def _nombre_valido(nombre):
        return isinstance(nombre, str) and bool(nombre)

    @staticmethod
    def _validar_aciclicidad(grafo):
        pendientes = {nombre: len(prerrequisitos) for nombre, prerrequisitos in grafo.items()}
        dependientes = {nombre: [] for nombre in grafo}
        for nombre, prerrequisitos in grafo.items():
            for prerrequisito in prerrequisitos:
                dependientes[prerrequisito].append(nombre)

        disponibles = [nombre for nombre, cantidad in pendientes.items() if cantidad == 0]
        procesados = 0
        while disponibles:
            nombre = disponibles.pop()
            procesados += 1
            for dependiente in dependientes[nombre]:
                pendientes[dependiente] -= 1
                if pendientes[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesados != len(grafo):
            raise ValueError("las dependencias contienen un ciclo")

    def estados(self):
        """Devuelve una copia de los estados actuales."""
        return self._estados.copy()

    def tomar(self):
        """Lanza tareas habilitadas hasta alcanzar la capacidad disponible."""
        lugares_libres = self._capacidad - sum(
            estado == self._EN_CURSO for estado in self._estados.values()
        )
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == self._PENDIENTE
            and all(self._estados[prerrequisito] == self._LISTO
                    for prerrequisito in self._dependencias[nombre])
        )
        nuevas = habilitadas[:lugares_libres]
        for nombre in nuevas:
            self._estados[nombre] = self._EN_CURSO
        return nuevas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea actualmente en curso."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not self._nombre_valido(nombre) or nombre not in self._estados or self._estados[nombre] != self._EN_CURSO:
            raise ValueError("la tarea debe estar en curso")

        self._estados[nombre] = self._LISTO if exito else self._FALLO
        if exito:
            return None

        por_revisar = list(self._dependientes[nombre])
        while por_revisar:
            dependiente = por_revisar.pop()
            if self._estados[dependiente] == self._PENDIENTE:
                self._estados[dependiente] = self._BLOQUEADO
                por_revisar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        """Indica si no quedan tareas pendientes ni en curso."""
        return all(
            estado in (self._LISTO, self._FALLO, self._BLOQUEADO)
            for estado in self._estados.values()
        )
