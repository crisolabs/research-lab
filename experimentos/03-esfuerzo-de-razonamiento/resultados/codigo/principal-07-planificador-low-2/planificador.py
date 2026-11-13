from collections import deque


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("Las dependencias deben ser un diccionario")

        nombres = list(dependencias)
        if any(not isinstance(nombre, str) or not nombre for nombre in nombres):
            raise ValueError("Los nombres deben ser strings no vacíos")

        copia = {}
        for nombre, requisitos in dependencias.items():
            try:
                requisitos = list(requisitos)
            except TypeError as error:
                raise ValueError("Los prerrequisitos deben ser iterables") from error
            if any(not isinstance(req, str) or not req for req in requisitos):
                raise ValueError("Los prerrequisitos deben tener nombres válidos")
            if any(req not in dependencias for req in requisitos):
                raise ValueError("Prerrequisito desconocido")
            copia[nombre] = set(requisitos)

        sucesores = {nombre: set() for nombre in nombres}
        restantes = {nombre: len(requisitos) for nombre, requisitos in copia.items()}
        for nombre, requisitos in copia.items():
            for requisito in requisitos:
                sucesores[requisito].add(nombre)
        disponibles = deque(nombre for nombre in nombres if restantes[nombre] == 0)
        visitados = 0
        while disponibles:
            nombre = disponibles.popleft()
            visitados += 1
            for sucesor in sucesores[nombre]:
                restantes[sucesor] -= 1
                if restantes[sucesor] == 0:
                    disponibles.append(sucesor)
        if visitados != len(nombres):
            raise ValueError("Las dependencias contienen un ciclo")

        self._dependencias = copia
        self._sucesores = sucesores
        self._capacidad = capacidad
        self._estados = {nombre: "pendiente" for nombre in sorted(nombres)}

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == "en_curso" for estado in self._estados.values()
        )
        nuevas = []
        for nombre, estado in self._estados.items():
            if len(nuevas) >= libres:
                break
            if estado == "pendiente" and all(
                self._estados[req] == "listo" for req in self._dependencias[nombre]
            ):
                self._estados[nombre] = "en_curso"
                nuevas.append(nombre)
        return nuevas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("Nombre desconocido")
        if not isinstance(exito, bool) or self._estados[nombre] != "en_curso":
            raise ValueError("Finalización inválida")
        self._estados[nombre] = "listo" if exito else "fallo"
        if not exito:
            pendientes = deque(self._sucesores[nombre])
            while pendientes:
                sucesor = pendientes.popleft()
                if self._estados[sucesor] == "pendiente":
                    self._estados[sucesor] = "bloqueado"
                    pendientes.extend(self._sucesores[sucesor])

    def terminado(self):
        return all(
            estado in ("listo", "fallo", "bloqueado")
            for estado in self._estados.values()
        )
