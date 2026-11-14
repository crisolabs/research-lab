"""Implementá el planificador pedido en TAREA.md."""

from collections.abc import Mapping

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINADOS = frozenset((LISTO, FALLO, BLOQUEADO))


def _es_nombre(valor):
    return isinstance(valor, str) and valor != ""


def _copiar_dependencias(dependencias):
    if not isinstance(dependencias, Mapping):
        raise ValueError("dependencias debe ser un diccionario")

    copia = {}
    for nombre, prerrequisitos in dependencias.items():
        if not _es_nombre(nombre):
            raise ValueError(f"nombre inválido: {nombre!r}")
        try:
            iterador = iter(prerrequisitos)
        except TypeError:
            raise ValueError(f"prerrequisitos no iterables: {nombre!r}") from None
        conjunto = set()
        for prerrequisito in iterador:
            if not _es_nombre(prerrequisito):
                raise ValueError(f"nombre inválido: {prerrequisito!r}")
            conjunto.add(prerrequisito)
        copia[nombre] = conjunto

    for prerrequisitos in copia.values():
        for prerrequisito in prerrequisitos:
            if prerrequisito not in copia:
                raise ValueError(f"referencia desconocida: {prerrequisito!r}")
    return copia


def _invertir(copia):
    dependientes = {nombre: set() for nombre in copia}
    for nombre, prerrequisitos in copia.items():
        for prerrequisito in prerrequisitos:
            dependientes[prerrequisito].add(nombre)
    return dependientes


def _verificar_aciclico(copia, dependientes):
    faltantes = {n: len(p) for n, p in copia.items()}
    sin_faltantes = [n for n, cantidad in faltantes.items() if cantidad == 0]
    procesados = 0
    while sin_faltantes:
        actual = sin_faltantes.pop()
        procesados += 1
        for dependiente in dependientes[actual]:
            faltantes[dependiente] -= 1
            if faltantes[dependiente] == 0:
                sin_faltantes.append(dependiente)
    if procesados != len(copia):
        raise ValueError("ciclo de dependencias")


def _validar_capacidad(capacidad):
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise ValueError("capacidad debe ser un entero positivo")
    capacidad = int(capacidad)
    if capacidad <= 0:
        raise ValueError("capacidad debe ser un entero positivo")
    return capacidad


class Planificador:
    def __init__(self, dependencias, capacidad):
        copia = _copiar_dependencias(dependencias)
        dependientes = _invertir(copia)
        _verificar_aciclico(copia, dependientes)
        capacidad = _validar_capacidad(capacidad)

        self._orden = tuple(sorted(copia))
        self._prerrequisitos = {n: frozenset(copia[n]) for n in self._orden}
        self._dependientes = {n: frozenset(dependientes[n]) for n in self._orden}
        self._estados = {n: PENDIENTE for n in self._orden}
        self._capacidad = capacidad

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        en_curso = sum(1 for estado in self._estados.values() if estado == EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        for nombre in self._orden:
            if libres <= 0:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._prerrequisitos[nombre]):
                self._estados[nombre] = EN_CURSO
                lanzadas.append(nombre)
                libres -= 1
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if exito:
            self._estados[nombre] = LISTO
        else:
            self._estados[nombre] = FALLO
            self._bloquear_dependientes(nombre)

    def terminado(self):
        return all(estado in _TERMINADOS for estado in self._estados.values())

    def _bloquear_dependientes(self, origen):
        pila = [origen]
        visitados = {origen}
        while pila:
            actual = pila.pop()
            for dependiente in self._dependientes[actual]:
                if dependiente in visitados:
                    continue
                visitados.add(dependiente)
                if self._estados[dependiente] == PENDIENTE:
                    self._estados[dependiente] = BLOQUEADO
                pila.append(dependiente)
