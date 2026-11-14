"""Planificador de tareas con dependencias: sólo administra estados."""

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class _ErrorDeTipo(TypeError, ValueError):
    """Argumento de tipo incorrecto (capturable como TypeError o ValueError)."""


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise _ErrorDeTipo("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _ErrorDeTipo("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        # Copia de la entrada (se itera cada iterable una sola vez).
        crudo = {}
        for nombre, prereqs in list(dependencias.items()):
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)):
                raise _ErrorDeTipo(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                )
            try:
                lista = list(prereqs)
            except TypeError:
                raise _ErrorDeTipo(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de nombres"
                ) from None
            crudo[nombre] = lista

        deps = {}
        for nombre, lista in crudo.items():
            for p in lista:
                if not _nombre_valido(p):
                    raise ValueError(f"nombre de prerrequisito inválido: {p!r}")
                if p not in crudo:
                    raise ValueError(f"prerrequisito desconocido: {p!r}")
            deps[nombre] = frozenset(lista)

        self._verificar_ciclos(deps)

        dependientes = {nombre: set() for nombre in deps}
        for nombre, ps in deps.items():
            for p in ps:
                dependientes[p].add(nombre)

        self._deps = deps
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = {nombre: PENDIENTE for nombre in sorted(deps)}

    @staticmethod
    def _verificar_ciclos(deps):
        # Algoritmo de Kahn (iterativo, sin límite de recursión).
        faltan = {n: len(ps) for n, ps in deps.items()}
        dependientes = {n: [] for n in deps}
        for n, ps in deps.items():
            for p in ps:
                dependientes[p].append(n)
        libres = [n for n, c in faltan.items() if c == 0]
        vistos = 0
        while libres:
            n = libres.pop()
            vistos += 1
            for d in dependientes[n]:
                faltan[d] -= 1
                if faltan[d] == 0:
                    libres.append(d)
        if vistos != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        est = self._estados
        libres = self._capacidad - sum(1 for e in est.values() if e == EN_CURSO)
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(est):
            if len(lanzadas) >= libres:
                break
            if est[nombre] == PENDIENTE and all(
                est[p] == LISTO for p in self._deps[nombre]
            ):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            est[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise _ErrorDeTipo("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        visitados = {nombre}
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if d in visitados:
                    continue
                visitados.add(d)
                if self._estados[d] == PENDIENTE:
                    self._estados[d] = BLOQUEADO
                pila.append(d)
        return None

    def terminado(self):
        return all(e in (LISTO, FALLO, BLOQUEADO) for e in self._estados.values())
