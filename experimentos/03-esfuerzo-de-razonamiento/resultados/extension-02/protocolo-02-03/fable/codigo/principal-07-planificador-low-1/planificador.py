"""Planificador de dependencias: sólo administra estados, no ejecuta nada."""

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        deps = {}
        for nombre, prereqs in dependencias.items():
            if not _nombre_valido(nombre):
                raise ValueError(f"nombre de tarea inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes, bytearray)):
                raise ValueError(f"las dependencias de {nombre!r} deben ser un iterable de nombres")
            try:
                lista = list(prereqs)
            except TypeError:
                raise ValueError(f"las dependencias de {nombre!r} no son iterables") from None
            for p in lista:
                if not _nombre_valido(p):
                    raise ValueError(f"nombre de dependencia inválido: {p!r}")
            deps[nombre] = frozenset(lista)

        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError(f"dependencia desconocida: {p!r} (requerida por {nombre!r})")

        # Detección de ciclos (Kahn, iterativo).
        dependientes = {n: [] for n in deps}
        faltan = {}
        for nombre, prereqs in deps.items():
            faltan[nombre] = len(prereqs)
            for p in prereqs:
                dependientes[p].append(nombre)
        cola = [n for n, c in faltan.items() if c == 0]
        vistos = 0
        while cola:
            n = cola.pop()
            vistos += 1
            for d in dependientes[n]:
                faltan[d] -= 1
                if faltan[d] == 0:
                    cola.append(d)
        if vistos != len(deps):
            raise ValueError("las dependencias contienen un ciclo")

        self._capacidad = capacidad
        self._deps = deps
        self._dependientes = dependientes
        self._estados = {n: PENDIENTE for n in deps}

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
            if est[nombre] == PENDIENTE and all(est[p] == LISTO for p in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            est[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
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
