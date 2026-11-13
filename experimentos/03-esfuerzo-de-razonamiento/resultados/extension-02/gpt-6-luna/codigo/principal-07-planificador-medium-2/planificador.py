"""Planificador de tareas con dependencias."""


class Planificador:
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

        tareas = {}
        try:
            elementos = list(dependencias.items())
            for nombre, requisitos in elementos:
                if not isinstance(nombre, str) or not nombre:
                    raise ValueError("nombre de tarea inválido")
                iterador = iter(requisitos)
                conjunto = set()
                for requisito in iterador:
                    if not isinstance(requisito, str) or not requisito:
                        raise ValueError("nombre de prerrequisito inválido")
                    conjunto.add(requisito)
                tareas[nombre] = conjunto
        except ValueError:
            raise
        except Exception as error:
            raise ValueError("dependencias inválidas") from error

        for requisitos in tareas.values():
            if not requisitos.issubset(tareas):
                raise ValueError("prerrequisito desconocido")

        # Una ordenación topológica también detecta ciclos y auto dependencias.
        pendientes = {nombre: len(requisitos) for nombre, requisitos in tareas.items()}
        sucesores = {nombre: [] for nombre in tareas}
        for nombre, requisitos in tareas.items():
            for requisito in requisitos:
                sucesores[requisito].append(nombre)
        disponibles = [nombre for nombre, cantidad in pendientes.items() if cantidad == 0]
        visitadas = 0
        while disponibles:
            nombre = disponibles.pop()
            visitadas += 1
            for sucesor in sucesores[nombre]:
                pendientes[sucesor] -= 1
                if pendientes[sucesor] == 0:
                    disponibles.append(sucesor)
        if visitadas != len(tareas):
            raise ValueError("el grafo contiene un ciclo")

        self._dependencias = tareas
        self._sucesores = sucesores
        self._capacidad = capacidad
        self._estados = {nombre: self._PENDIENTE for nombre in tareas}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == self._EN_CURSO for estado in self._estados.values()
        )
        if libres <= 0:
            return []
        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == self._PENDIENTE
            and all(self._estados[requisito] == self._LISTO
                    for requisito in self._dependencias[nombre])
        )
        nuevas = habilitadas[:libres]
        for nombre in nuevas:
            self._estados[nombre] = self._EN_CURSO
        return nuevas

    def completar(self, nombre, exito=True):
        if (not isinstance(nombre, str) or nombre not in self._estados
                or self._estados[nombre] != self._EN_CURSO
                or not isinstance(exito, bool)):
            raise ValueError("completado inválido")

        if exito:
            self._estados[nombre] = self._LISTO
            return None

        self._estados[nombre] = self._FALLO
        por_revisar = list(self._sucesores[nombre])
        visitados = set()
        while por_revisar:
            sucesor = por_revisar.pop()
            if sucesor in visitados:
                continue
            visitados.add(sucesor)
            if self._estados[sucesor] == self._PENDIENTE:
                self._estados[sucesor] = self._BLOQUEADO
                por_revisar.extend(self._sucesores[sucesor])
        return None

    def terminado(self):
        return all(
            estado in (self._LISTO, self._FALLO, self._BLOQUEADO)
            for estado in self._estados.values()
        )
