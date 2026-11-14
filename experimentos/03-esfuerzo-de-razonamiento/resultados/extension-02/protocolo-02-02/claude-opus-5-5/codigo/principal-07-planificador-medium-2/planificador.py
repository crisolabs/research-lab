"""Planificador de dependencias (ver TAREA.md)."""

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        deps = {}
        for nombre, prereqs in list(dependencias.items()):
            if not isinstance(nombre, str) or not nombre:
                raise ValueError(f"nombre inválido: {nombre!r}")
            if isinstance(prereqs, (str, bytes)):
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}")
            try:
                lista = list(prereqs)
            except TypeError:
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}") from None
            conjunto = set()
            for p in lista:
                if not isinstance(p, str) or not p:
                    raise ValueError(f"prerrequisito inválido: {p!r}")
                conjunto.add(p)
            deps[nombre] = frozenset(conjunto)

        for nombre, prereqs in deps.items():
            for p in prereqs:
                if p not in deps:
                    raise ValueError(f"referencia desconocida: {p!r}")

        # Detección de ciclos (DFS iterativo, incluye auto dependencia).
        color = {n: 0 for n in deps}  # 0 blanco, 1 gris, 2 negro
        for inicio in sorted(deps):
            if color[inicio]:
                continue
            color[inicio] = 1
            pila = [(inicio, iter(sorted(deps[inicio])))]
            while pila:
                nodo, it = pila[-1]
                siguiente = next(it, None)
                if siguiente is None:
                    color[nodo] = 2
                    pila.pop()
                elif color[siguiente] == 1:
                    raise ValueError(f"ciclo detectado en {siguiente!r}")
                elif color[siguiente] == 0:
                    color[siguiente] = 1
                    pila.append((siguiente, iter(sorted(deps[siguiente]))))

        dependientes = {n: set() for n in deps}
        for nombre, prereqs in deps.items():
            for p in prereqs:
                dependientes[p].add(nombre)

        self._deps = deps
        self._dependientes = {n: frozenset(s) for n, s in dependientes.items()}
        self._capacidad = capacidad
        self._estados = {n: PENDIENTE for n in deps}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
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
            if all(self._estados[p] == LISTO for p in self._deps[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
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
