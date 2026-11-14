"""Planificador de tareas con dependencias (sólo administra estados)."""

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra el estado de un grafo de tareas con capacidad limitada."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise ValueError("capacidad debe ser un entero")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser positiva")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        # Validación completa antes de modificar nada.
        grafo = {}
        for nombre, prereqs in dependencias.items():
            _validar_nombre(nombre)
            if isinstance(prereqs, (str, bytes)):
                raise ValueError("prerrequisitos deben ser un iterable de nombres")
            try:
                items = list(prereqs)
            except TypeError:
                raise ValueError("prerrequisitos deben ser un iterable de nombres")
            grafo[nombre] = frozenset(_validar_nombre(p) for p in items)

        for nombre, prereqs in grafo.items():
            for p in prereqs:
                if p not in grafo:
                    raise ValueError(f"referencia desconocida: {p!r}")

        self._verificar_aciclico(grafo)

        self._dependencias = grafo
        self._dependientes = {n: set() for n in grafo}
        for nombre, prereqs in grafo.items():
            for p in prereqs:
                self._dependientes[p].add(nombre)
        self._estados = {n: PENDIENTE for n in grafo}
        self._capacidad = capacidad

    @staticmethod
    def _verificar_aciclico(grafo):
        # Algoritmo de Kahn: si no se pueden ordenar todos los nodos, hay ciclo.
        restantes = {n: len(p) for n, p in grafo.items()}
        dependientes = {n: [] for n in grafo}
        for nombre, prereqs in grafo.items():
            for p in prereqs:
                dependientes[p].append(nombre)
        cola = [n for n, c in restantes.items() if c == 0]
        visitados = 0
        while cola:
            n = cola.pop()
            visitados += 1
            for d in dependientes[n]:
                restantes[d] -= 1
                if restantes[d] == 0:
                    cola.append(d)
        if visitados != len(grafo):
            raise ValueError("el grafo contiene ciclos")

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza nuevas tareas habilitadas hasta llenar la capacidad libre."""
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._dependencias[nombre]):
                self._estados[nombre] = EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como terminada con éxito o fallida."""
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pendientes = [nombre]
        while pendientes:
            actual = pendientes.pop()
            for d in self._dependientes[actual]:
                if self._estados[d] == PENDIENTE:
                    self._estados[d] = BLOQUEADO
                    pendientes.append(d)
        return None

    def terminado(self):
        """Indica si todas las tareas alcanzaron un estado final."""
        return all(e in _TERMINALES for e in self._estados.values())
