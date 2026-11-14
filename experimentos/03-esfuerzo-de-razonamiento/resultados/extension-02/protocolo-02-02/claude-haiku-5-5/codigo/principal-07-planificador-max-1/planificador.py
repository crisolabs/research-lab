"""Implementá el planificador pedido en TAREA.md."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINADOS = frozenset({LISTO, FALLO, BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    def __init__(self, dependencias, capacidad):
        if (
            not isinstance(capacidad, int)
            or isinstance(capacidad, bool)
            or capacidad <= 0
        ):
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, Mapping):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia independiente de la entrada: cada iterable se consume una vez
        # y se guarda como frozenset, así las repeticiones se ignoran.
        copia = {}
        for nombre, prerrequisitos in dependencias.items():
            _validar_nombre(nombre)
            try:
                iterador = iter(prerrequisitos)
            except TypeError:
                raise ValueError(
                    f"prerrequisitos no iterables para {nombre!r}"
                ) from None
            copia[nombre] = frozenset(_validar_nombre(p) for p in iterador)

        orden = sorted(copia)
        for nombre in orden:
            for p in copia[nombre]:
                if p not in copia:
                    raise ValueError(
                        f"referencia desconocida {p!r} en {nombre!r}"
                    )

        grado = {}
        dependientes = {n: set() for n in orden}
        for nombre in orden:
            grado[nombre] = len(copia[nombre])
            for p in copia[nombre]:
                dependientes[p].add(nombre)

        # Kahn: una auto dependencia o un ciclo deja nodos sin ordenar.
        cola = [n for n in orden if grado[n] == 0]
        ordenados = 0
        while cola:
            actual = cola.pop()
            ordenados += 1
            for d in dependientes[actual]:
                grado[d] -= 1
                if grado[d] == 0:
                    cola.append(d)
        if ordenados != len(orden):
            raise ValueError("ciclo de dependencias")

        self._capacidad = capacidad
        self._prerrequisitos = {n: copia[n] for n in orden}
        self._dependientes = dependientes
        self._estado = {n: PENDIENTE for n in orden}

    def estados(self):
        return dict(self._estado)

    def tomar(self):
        activas = sum(1 for e in self._estado.values() if e == EN_CURSO)
        libres = self._capacidad - activas
        lanzadas = []
        for nombre in self._prerrequisitos:  # orden lexicográfico
            if len(lanzadas) >= libres:
                break
            if self._estado[nombre] == PENDIENTE and all(
                self._estado[p] == LISTO for p in self._prerrequisitos[nombre]
            ):
                self._estado[nombre] = EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estado:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estado[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")

        if exito:
            self._estado[nombre] = LISTO
            return

        self._estado[nombre] = FALLO
        pila = [nombre]
        vistos = {nombre}
        while pila:
            actual = pila.pop()
            for d in self._dependientes[actual]:
                if d not in vistos:
                    vistos.add(d)
                    if self._estado[d] == PENDIENTE:
                        self._estado[d] = BLOQUEADO
                    pila.append(d)

    def terminado(self):
        return all(e in _TERMINADOS for e in self._estado.values())
