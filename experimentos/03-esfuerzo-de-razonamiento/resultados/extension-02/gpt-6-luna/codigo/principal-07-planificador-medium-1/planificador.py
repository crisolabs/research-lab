"""Planificación de tareas según sus dependencias."""


class Planificador:
    """Administra estados de tareas sin ejecutarlas."""

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

        copia = {}
        for nombre, requisitos in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres deben ser strings no vacíos")
            try:
                iterador = iter(requisitos)
            except TypeError as error:
                raise ValueError("los prerrequisitos deben ser iterables") from error

            vistos = set()
            lista = []
            for requisito in iterador:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                if requisito not in vistos:
                    vistos.add(requisito)
                    lista.append(requisito)
            copia[nombre] = tuple(lista)

        for requisitos in copia.values():
            if any(requisito not in copia for requisito in requisitos):
                raise ValueError("prerrequisito desconocido")

        # Una ordenación topológica también detecta auto dependencias y ciclos.
        pendientes = {nombre: len(requisitos) for nombre, requisitos in copia.items()}
        siguientes = {nombre: [] for nombre in copia}
        for nombre, requisitos in copia.items():
            for requisito in requisitos:
                siguientes[requisito].append(nombre)
        disponibles = [nombre for nombre, cantidad in pendientes.items() if cantidad == 0]
        procesados = 0
        while disponibles:
            nombre = disponibles.pop()
            procesados += 1
            for dependiente in siguientes[nombre]:
                pendientes[dependiente] -= 1
                if pendientes[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesados != len(copia):
            raise ValueError("el grafo contiene un ciclo")

        self._dependencias = copia
        self._capacidad = capacidad
        self._estados = {nombre: self._PENDIENTE for nombre in copia}
        self._dependientes = siguientes

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == self._EN_CURSO for estado in self._estados.values()
        )
        if libres <= 0:
            return []

        elegibles = sorted(
            nombre
            for nombre, requisitos in self._dependencias.items()
            if self._estados[nombre] == self._PENDIENTE
            and all(self._estados[requisito] == self._LISTO for requisito in requisitos)
        )
        lanzadas = elegibles[:libres]
        for nombre in lanzadas:
            self._estados[nombre] = self._EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if (
            not isinstance(nombre, str)
            or nombre not in self._estados
            or self._estados[nombre] != self._EN_CURSO
        ):
            raise ValueError("la tarea no está en curso")

        if exito:
            self._estados[nombre] = self._LISTO
            return None

        self._estados[nombre] = self._FALLO
        por_visitar = list(self._dependientes[nombre])
        vistos = set()
        while por_visitar:
            dependiente = por_visitar.pop()
            if dependiente in vistos:
                continue
            vistos.add(dependiente)
            if self._estados[dependiente] == self._PENDIENTE:
                self._estados[dependiente] = self._BLOQUEADO
                por_visitar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        return all(
            estado in (self._LISTO, self._FALLO, self._BLOQUEADO)
            for estado in self._estados.values()
        )
