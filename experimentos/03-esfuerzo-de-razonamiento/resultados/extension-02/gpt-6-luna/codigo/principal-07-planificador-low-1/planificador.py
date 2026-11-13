"""Planificador de tareas con dependencias."""


class Planificador:
    """Administra el estado de tareas según sus prerrequisitos."""

    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    LISTO = "listo"
    FALLO = "fallo"
    BLOQUEADO = "bloqueado"

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        try:
            items = list(dependencias.items())
        except (AttributeError, TypeError):
            raise ValueError("dependencias debe ser un diccionario") from None

        prerequisitos = {}
        for nombre, requisitos in items:
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("los nombres deben ser strings no vacíos")
            try:
                valores = list(requisitos)
            except TypeError:
                raise ValueError("los prerrequisitos deben ser iterables") from None
            if any(not isinstance(req, str) or not req for req in valores):
                raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
            prerequisitos[nombre] = set(valores)

        nombres = set(prerequisitos)
        for requisitos in prerequisitos.values():
            if not requisitos <= nombres:
                raise ValueError("prerrequisito desconocido")

        # Una búsqueda en profundidad detecta tanto ciclos como auto dependencias.
        visitados = set()
        en_pila = set()

        def visitar(nombre):
            if nombre in en_pila:
                raise ValueError("el grafo contiene un ciclo")
            if nombre in visitados:
                return
            en_pila.add(nombre)
            for requisito in prerequisitos[nombre]:
                visitar(requisito)
            en_pila.remove(nombre)
            visitados.add(nombre)

        for nombre in prerequisitos:
            visitar(nombre)

        self._prerequisitos = prerequisitos
        self._estados = {nombre: self.PENDIENTE for nombre in prerequisitos}
        self._capacidad = capacidad

    def estados(self):
        return self._estados.copy()

    def tomar(self):
        libres = self._capacidad - sum(
            estado == self.EN_CURSO for estado in self._estados.values()
        )
        if libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == self.PENDIENTE
            and all(self._estados[req] == self.LISTO for req in self._prerequisitos[nombre])
        )[:libres]
        for nombre in habilitadas:
            self._estados[nombre] = self.EN_CURSO
        return habilitadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if nombre not in self._estados or self._estados[nombre] != self.EN_CURSO:
            raise ValueError("la tarea debe existir y estar en curso")

        if exito:
            self._estados[nombre] = self.LISTO
            return None

        self._estados[nombre] = self.FALLO
        pendientes = [nombre]
        while pendientes:
            fallida = pendientes.pop()
            for tarea, requisitos in self._prerequisitos.items():
                if (
                    self._estados[tarea] == self.PENDIENTE
                    and fallida in requisitos
                ):
                    self._estados[tarea] = self.BLOQUEADO
                    pendientes.append(tarea)
        return None

    def terminado(self):
        return all(
            estado in (self.LISTO, self.FALLO, self.BLOQUEADO)
            for estado in self._estados.values()
        )
