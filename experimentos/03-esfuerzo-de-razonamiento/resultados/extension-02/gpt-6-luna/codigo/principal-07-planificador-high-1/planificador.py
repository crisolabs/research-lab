"""Planificador sencillo de tareas con dependencias."""


class Planificador:
    """Administra el estado de un conjunto de tareas acíclico."""

    _PENDIENTE = "pendiente"
    _EN_CURSO = "en_curso"
    _LISTO = "listo"
    _FALLO = "fallo"
    _BLOQUEADO = "bloqueado"

    def __init__(self, dependencias, capacidad):
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        nombres = list(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("los nombres de tareas deben ser strings no vacíos")

        conjunto_nombres = set(nombres)
        prerrequisitos = {}
        for nombre in nombres:
            try:
                iterador = iter(dependencias[nombre])
            except TypeError as error:
                raise ValueError("los prerrequisitos deben ser iterables") from error

            requisitos = set()
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                if requisito not in conjunto_nombres:
                    raise ValueError("prerrequisito desconocido")
                requisitos.add(requisito)
            prerrequisitos[nombre] = requisitos

        # Kahn detecta ciclos, incluyendo las auto dependencias.
        restantes = {nombre: len(reqs) for nombre, reqs in prerrequisitos.items()}
        dependientes = {nombre: set() for nombre in nombres}
        for nombre, requisitos in prerrequisitos.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        disponibles = [nombre for nombre, cuenta in restantes.items() if cuenta == 0]
        procesadas = 0
        while disponibles:
            nombre = disponibles.pop()
            procesadas += 1
            for dependiente in dependientes[nombre]:
                restantes[dependiente] -= 1
                if restantes[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesadas != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._dependencias = prerrequisitos
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = {nombre: self._PENDIENTE for nombre in nombres}

    def estados(self):
        """Devuelve una copia del mapa de estados actual."""
        return self._estados.copy()

    def tomar(self):
        """Inicia tareas habilitadas hasta alcanzar la capacidad disponible."""
        lugares_libres = self._capacidad - sum(
            estado == self._EN_CURSO for estado in self._estados.values()
        )
        if lugares_libres <= 0:
            return []

        nuevas = []
        for nombre in sorted(self._estados):
            if self._estados[nombre] != self._PENDIENTE:
                continue
            if all(
                self._estados[requisito] == self._LISTO
                for requisito in self._dependencias[nombre]
            ):
                self._estados[nombre] = self._EN_CURSO
                nuevas.append(nombre)
                if len(nuevas) == lugares_libres:
                    break
        return nuevas

    def completar(self, nombre, exito=True):
        """Completa una tarea en curso y propaga bloqueos si falla."""
        if (
            not isinstance(nombre, str)
            or nombre not in self._estados
            or self._estados[nombre] != self._EN_CURSO
        ):
            raise ValueError("la tarea debe existir y estar en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = self._LISTO
            return None

        self._estados[nombre] = self._FALLO
        por_revisar = list(self._dependientes[nombre])
        vistos = set()
        while por_revisar:
            dependiente = por_revisar.pop()
            if dependiente in vistos:
                continue
            vistos.add(dependiente)
            if self._estados[dependiente] == self._PENDIENTE:
                self._estados[dependiente] = self._BLOQUEADO
            if self._estados[dependiente] in (self._BLOQUEADO, self._FALLO):
                por_revisar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        """Indica si todas las tareas alcanzaron un estado final."""
        finales = (self._LISTO, self._FALLO, self._BLOQUEADO)
        return all(estado in finales for estado in self._estados.values())
