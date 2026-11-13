"""Planificador de tareas con dependencias y capacidad limitada."""


class Planificador:
    """Administra los estados de tareas sin ejecutarlas."""

    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    LISTO = "listo"
    FALLO = "fallo"
    BLOQUEADO = "bloqueado"

    _ESTADOS_TERMINALES = frozenset((LISTO, FALLO, BLOQUEADO))

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        # Construir copias locales primero hace que una entrada inválida no deje
        # ningún estado parcialmente inicializado.
        nombres = set()
        dependencias_copiadas = {}
        try:
            elementos = dependencias.items()
            for nombre, prerrequisitos in elementos:
                if not isinstance(nombre, str) or not nombre:
                    raise ValueError("los nombres de tareas deben ser strings no vacíos")
                nombres.add(nombre)
                try:
                    dependencias_copiadas[nombre] = frozenset(prerrequisitos)
                except TypeError as exc:
                    raise ValueError("los prerrequisitos deben ser iterables de nombres") from exc
        except ValueError:
            raise

        for prerrequisitos in dependencias_copiadas.values():
            for requisito in prerrequisitos:
                if not isinstance(requisito, str) or not requisito:
                    raise ValueError("los nombres de prerrequisitos deben ser strings no vacíos")
                if requisito not in nombres:
                    raise ValueError("hay un prerrequisito desconocido")

        dependientes = {nombre: set() for nombre in nombres}
        cantidades = {}
        for nombre, prerrequisitos in dependencias_copiadas.items():
            cantidades[nombre] = len(prerrequisitos)
            for requisito in prerrequisitos:
                dependientes[requisito].add(nombre)

        # Kahn detecta ciclos sin depender de la profundidad de recursión.
        disponibles = [nombre for nombre, cantidad in cantidades.items() if cantidad == 0]
        procesadas = 0
        indice = 0
        while indice < len(disponibles):
            nombre = disponibles[indice]
            indice += 1
            procesadas += 1
            for dependiente in dependientes[nombre]:
                cantidades[dependiente] -= 1
                if cantidades[dependiente] == 0:
                    disponibles.append(dependiente)
        if procesadas != len(nombres):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._dependencias = {
            nombre: frozenset(prerrequisitos)
            for nombre, prerrequisitos in dependencias_copiadas.items()
        }
        self._dependientes = {
            nombre: frozenset(nombres_dependientes)
            for nombre, nombres_dependientes in dependientes.items()
        }
        self._estados = {nombre: self.PENDIENTE for nombre in nombres}

    def estados(self):
        """Devuelve una copia de los estados actuales."""
        return self._estados.copy()

    def tomar(self):
        """Inicia hasta llenar la capacidad con tareas actualmente habilitadas."""
        lugares_libres = self._capacidad - sum(
            estado == self.EN_CURSO for estado in self._estados.values()
        )
        if lugares_libres <= 0:
            return []

        habilitadas = sorted(
            nombre
            for nombre, estado in self._estados.items()
            if estado == self.PENDIENTE
            and all(
                self._estados[requisito] == self.LISTO
                for requisito in self._dependencias[nombre]
            )
        )
        tomadas = habilitadas[:lugares_libres]
        for nombre in tomadas:
            self._estados[nombre] = self.EN_CURSO
        return tomadas

    def completar(self, nombre, exito=True):
        """Finaliza una tarea en curso y propaga bloqueos si falla."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("nombre de tarea desconocido")
        if self._estados[nombre] != self.EN_CURSO:
            raise ValueError("la tarea no está en curso")

        if exito:
            self._estados[nombre] = self.LISTO
            return None

        self._estados[nombre] = self.FALLO
        pendientes_por_revisar = list(self._dependientes[nombre])
        visitados = set()
        while pendientes_por_revisar:
            dependiente = pendientes_por_revisar.pop()
            if dependiente in visitados:
                continue
            visitados.add(dependiente)
            if self._estados[dependiente] == self.PENDIENTE:
                self._estados[dependiente] = self.BLOQUEADO
            pendientes_por_revisar.extend(self._dependientes[dependiente])
        return None

    def terminado(self):
        """Indica si todas las tareas alcanzaron un estado terminal."""
        return all(estado in self._ESTADOS_TERMINALES for estado in self._estados.values())
