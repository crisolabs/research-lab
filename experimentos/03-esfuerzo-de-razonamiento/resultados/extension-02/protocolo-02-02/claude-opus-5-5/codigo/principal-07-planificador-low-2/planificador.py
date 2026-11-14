"""Planificador de dependencias."""

_ESTADOS_FINALES = ("listo", "fallo", "bloqueado")


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        deps = {}
        for nombre, prereqs in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("nombre inválido")
            if isinstance(prereqs, (str, bytes)):
                raise ValueError("los prerrequisitos deben ser un iterable de nombres")
            try:
                lista = list(prereqs)
            except TypeError:
                raise ValueError("prerrequisitos no iterables") from None
            conjunto = set()
            for p in lista:
                if not isinstance(p, str) or not p:
                    raise ValueError("nombre de prerrequisito inválido")
                conjunto.add(p)
            deps[nombre] = frozenset(conjunto)
        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError(f"referencia desconocida: {p!r}")
        # Detección de ciclos (iterativa).
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
                    raise ValueError("ciclo de dependencias")
                elif color[sig] == 0:
                    color[sig] = 1
                    pila.append((sig, iter(sorted(deps[sig]))))
        self._deps = deps
        self._dependientes = {n: set() for n in deps}
        for n, ps in deps.items():
            for p in ps:
                self._dependientes[p].add(n)
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
        for n in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[n] == "pendiente" and all(
                self._estados[p] == "listo" for p in self._deps[n]
            ):
                lanzadas.append(n)
        for n in lanzadas:
            self._estados[n] = "en_curso"
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")
        if exito:
            self._estados[nombre] = "listo"
            return None
        self._estados[nombre] = "fallo"
        pila = [nombre]
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if self._estados[d] == "pendiente":
                    self._estados[d] = "bloqueado"
                    pila.append(d)
        return None

    def terminado(self):
        return all(e in _ESTADOS_FINALES for e in self._estados.values())
