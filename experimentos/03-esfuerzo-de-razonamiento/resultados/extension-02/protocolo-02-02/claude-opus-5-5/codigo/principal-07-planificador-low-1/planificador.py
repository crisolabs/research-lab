class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser dict")
        if type(capacidad) is not int or capacidad <= 0:
            raise ValueError("capacidad inválida")
        deps = {}
        for nombre, reqs in dependencias.items():
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("nombre inválido")
            if isinstance(reqs, (str, bytes)):
                raise ValueError("prerrequisitos inválidos")
            try:
                lista = list(reqs)
            except TypeError:
                raise ValueError("prerrequisitos no iterables")
            conj = set()
            for r in lista:
                if not isinstance(r, str) or not r:
                    raise ValueError("prerrequisito inválido")
                conj.add(r)
            deps[nombre] = frozenset(conj)
        for nombre, reqs in deps.items():
            for r in reqs:
                if r not in deps:
                    raise ValueError("referencia desconocida: %r" % r)
        # detección de ciclos (iterativa)
        color = {n: 0 for n in deps}
        for inicio in sorted(deps):
            if color[inicio]:
                continue
            pila = [(inicio, iter(sorted(deps[inicio])))]
            color[inicio] = 1
            while pila:
                n, it = pila[-1]
                sig = next(it, None)
                if sig is None:
                    color[n] = 2
                    pila.pop()
                elif color[sig] == 1:
                    raise ValueError("ciclo detectado")
                elif color[sig] == 0:
                    color[sig] = 1
                    pila.append((sig, iter(sorted(deps[sig]))))
        self._deps = deps
        self._dependientes = {n: set() for n in deps}
        for n, reqs in deps.items():
            for r in reqs:
                self._dependientes[r].add(n)
        self._capacidad = capacidad
        self._estados = {n: "pendiente" for n in deps}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        libres = self._capacidad - sum(
            1 for e in self._estados.values() if e == "en_curso")
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for n in sorted(self._deps):
            if len(lanzadas) >= libres:
                break
            if self._estados[n] == "pendiente" and all(
                    self._estados[r] == "listo" for r in self._deps[n]):
                lanzadas.append(n)
        for n in lanzadas:
            self._estados[n] = "en_curso"
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida")
        if type(exito) is not bool:
            raise ValueError("exito debe ser bool")
        if self._estados[nombre] != "en_curso":
            raise ValueError("la tarea no está en curso")
        if exito:
            self._estados[nombre] = "listo"
            return None
        self._estados[nombre] = "fallo"
        pila = [nombre]
        vistos = {nombre}
        while pila:
            n = pila.pop()
            for d in self._dependientes[n]:
                if d in vistos:
                    continue
                vistos.add(d)
                if self._estados[d] == "pendiente":
                    self._estados[d] = "bloqueado"
                pila.append(d)
        return None

    def terminado(self):
        return all(e in ("listo", "fallo", "bloqueado")
                   for e in self._estados.values())
