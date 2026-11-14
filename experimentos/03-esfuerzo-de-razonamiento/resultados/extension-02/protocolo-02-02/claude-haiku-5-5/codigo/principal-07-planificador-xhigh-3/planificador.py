"""Implementá el planificador pedido en TAREA.md."""

from collections.abc import Iterable, Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"


def _es_nombre(valor):
    return isinstance(valor, str) and valor != ""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")

        # Copia validada: prerrequisitos como frozenset (repeticiones ignoradas).
        prerrequisitos = {}
        for nombre, requisitos in dependencias.items():
            if not _es_nombre(nombre):
                raise ValueError(f"nombre inválido: {nombre!r}")
            if not isinstance(requisitos, Iterable):
                raise ValueError(f"prerrequisitos inválidos para {nombre!r}")
            conjunto = set()
            for requisito in requisitos:
                if not _es_nombre(requisito):
                    raise ValueError(f"prerrequisito inválido: {requisito!r}")
                conjunto.add(requisito)
            prerrequisitos[nombre] = frozenset(conjunto)

        for nombre, requisitos in prerrequisitos.items():
            for requisito in requisitos:
                if requisito not in prerrequisitos:
                    raise ValueError(
                        f"referencia desconocida: {nombre!r} depende de {requisito!r}"
                    )

        # Detección de ciclos (Kahn): si no se procesan todos los nodos, hay ciclo.
        # Una auto dependencia nunca llega a grado cero, así que también se detecta.
        dependientes = {nombre: set() for nombre in prerrequisitos}
        for nombre, requisitos in prerrequisitos.items():
            for requisito in requisitos:
                dependientes[requisito].add(nombre)

        restantes = {nombre: len(reqs) for nombre, reqs in prerrequisitos.items()}
        cola = [nombre for nombre, n in restantes.items() if n == 0]
        procesados = 0
        while cola:
            actual = cola.pop()
            procesados += 1
            for dep in dependientes[actual]:
                restantes[dep] -= 1
                if restantes[dep] == 0:
                    cola.append(dep)
        if procesados != len(prerrequisitos):
            raise ValueError("el grafo de dependencias contiene ciclos")

        # Todo validado: recién ahora se almacena el estado.
        orden = sorted(prerrequisitos)
        self._prerrequisitos = {n: prerrequisitos[n] for n in orden}
        self._dependientes = {n: frozenset(dependientes[n]) for n in orden}
        self._capacidad = int(capacidad)
        self._estados = {n: PENDIENTE for n in orden}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for e in self._estados.values() if e == EN_CURSO)
        libres = self._capacidad - en_curso
        if libres <= 0:
            return []

        habilitadas = [
            nombre
            for nombre in sorted(self._estados)
            if self._estados[nombre] == PENDIENTE
            and all(self._estados[p] == LISTO for p in self._prerrequisitos[nombre])
        ]
        lanzadas = habilitadas[:libres]
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso (estado: {self._estados[nombre]})"
            )
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser un bool")

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        pila = [nombre]
        visitados = {nombre}
        while pila:
            actual = pila.pop()
            for dep in self._dependientes[actual]:
                if dep in visitados:
                    continue
                visitados.add(dep)
                if self._estados[dep] == PENDIENTE:
                    self._estados[dep] = BLOQUEADO
                pila.append(dep)
        return None

    def terminado(self):
        return all(e in (LISTO, FALLO, BLOQUEADO) for e in self._estados.values())
