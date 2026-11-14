"""Planificador de dependencias con capacidad limitada."""

_ESTADOS_FINALES = ("listo", "fallo", "bloqueado")


def _nombre_valido(nombre):
    return isinstance(nombre, str) and nombre != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        deps = {}
        for nombre, prereqs in dependencias.items():
            if not _nombre_valido(nombre):
                raise ValueError("nombre inválido: %r" % (nombre,))
            if isinstance(prereqs, (str, bytes)):
                raise ValueError("prerrequisitos deben ser un iterable de nombres")
            try:
                lista = list(prereqs)
            except TypeError:
                raise ValueError("prerrequisitos deben ser iterables") from None
            conjunto = set()
            for p in lista:
                if not _nombre_valido(p):
                    raise ValueError("nombre de prerrequisito inválido: %r" % (p,))
                conjunto.add(p)
            deps[nombre] = frozenset(conjunto)

        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError("referencia desconocida: %r" % (p,))

        # Detección de ciclos (DFS iterativo).
        color = {n: 0 for n in deps}
        for inicio in sorted(deps):
            if color[inicio]:
                continue
            color[inicio] = 1
            pila = [(inicio, iter(sorted(deps[inicio])))]
            while pila:
                nodo, it = pila[-1]
                sig = next(it, None)
                if sig is None:
                    color[nodo] = 2
                    pila.pop()
                elif color[sig] == 1:
                    raise ValueError("ciclo detectado en %r" % (sig,))
                elif color[sig] == 0:
                    color[sig] = 1
                    pila.append((sig, iter(sorted(deps[sig]))))

        dependientes = {n: set() for n in deps}
        for nombre, prereqs in deps.items():
            for p in prereqs:
                dependientes[p].add(nombre)

        self._deps = deps
        self._dependientes = dependientes
        self._capacidad = capacidad
        self._estados = {n: "pendiente" for n in deps}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == "en_curso")
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._deps):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != "pendiente":
                continue
            if all(self._estados[p] == "listo" for p in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = "en_curso"
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida: %r" % (nombre,))
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea %r no está en curso" % (nombre,))
        if exito:
            self._estados[nombre] = "listo"
            return None
        self._estados[nombre] = "fallo"
        pila = [nombre]
        vistos = {nombre}
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if d in vistos:
                    continue
                vistos.add(d)
                if self._estados[d] == "pendiente":
                    self._estados[d] = "bloqueado"
                pila.append(d)
        return None

    def terminado(self):
        return all(e in _ESTADOS_FINALES for e in self._estados.values())
