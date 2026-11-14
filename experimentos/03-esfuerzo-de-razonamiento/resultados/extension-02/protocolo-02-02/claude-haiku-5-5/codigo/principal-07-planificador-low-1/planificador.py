"""Planificador de tareas con dependencias, según TAREA.md."""

from collections import deque

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"

_TERMINALES = frozenset({_LISTO, _FALLO, _BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or nombre == "":
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


def _validar_capacidad(capacidad):
    if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
        raise ValueError(f"capacidad inválida: {capacidad!r}")
    return capacidad


class Planificador:
    """Administra estados de tareas con dependencias; no ejecuta nada."""

    def __init__(self, dependencias, capacidad):
        self._capacidad = _validar_capacidad(capacidad)
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia interna: nombre -> frozenset de prerrequisitos (sin repeticiones).
        deps = {}
        for nombre, prerrequisitos in dependencias.items():
            _validar_nombre(nombre)
            if not isinstance(prerrequisitos, (list, tuple, set, frozenset)) and not hasattr(
                prerrequisitos, "__iter__"
            ):
                raise ValueError(f"dependencias no iterables para {nombre!r}")
            deps[nombre] = frozenset(_validar_nombre(p) for p in prerrequisitos)

        # Referencias desconocidas.
        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError(f"referencia desconocida: {p!r} en {nombre!r}")

        # Ciclos (incluye auto dependencia), mediante Kahn.
        grados = {n: len(p) for n, p in deps.items()}
        dependientes = {n: [] for n in deps}
        for n, prereqs in deps.items():
            for p in prereqs:
                dependientes[p].append(n)
        cola = deque(n for n, g in grados.items() if g == 0)
        visitados = 0
        while cola:
            actual = cola.popleft()
            visitados += 1
            for d in dependientes[actual]:
                grados[d] -= 1
                if grados[d] == 0:
                    cola.append(d)
        if visitados != len(deps):
            raise ValueError("el grafo contiene ciclos")

        self._deps = deps
        self._dependientes = dependientes
        self._estados = {n: _PENDIENTE for n in deps}
        self._en_curso = 0

    def estados(self):
        """Copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza nuevas tareas habilitadas hasta llenar la capacidad libre."""
        libres = self._capacidad - self._en_curso
        if libres <= 0:
            return []
        candidatas = sorted(
            n
            for n, estado in self._estados.items()
            if estado == _PENDIENTE
            and all(self._estados[p] == _LISTO for p in self._deps[n])
        )
        lanzadas = candidatas[:libres]
        for n in lanzadas:
            self._estados[n] = _EN_CURSO
        self._en_curso += len(lanzadas)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Marca una tarea en curso como listo (éxito) o fallo (bloqueando dependientes)."""
        if not isinstance(exito, bool):
            raise ValueError(f"exito debe ser bool: {exito!r}")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != _EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        self._en_curso -= 1
        if exito:
            self._estados[nombre] = _LISTO
            return None

        self._estados[nombre] = _FALLO
        pendientes = deque([nombre])
        while pendientes:
            actual = pendientes.popleft()
            for d in self._dependientes[actual]:
                if self._estados[d] == _PENDIENTE:
                    self._estados[d] = _BLOQUEADO
                    pendientes.append(d)
        return None

    def terminado(self):
        """True si todas las tareas están en un estado terminal."""
        return all(estado in _TERMINALES for estado in self._estados.values())
