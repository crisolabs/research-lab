"""Planificador de dependencias: sólo administra estados de tareas."""

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_FINALES = frozenset((LISTO, FALLO, BLOQUEADO))


class _ErrorDeTipo(ValueError, TypeError):
    """Argumento de tipo incorrecto (es ValueError y también TypeError)."""


class Planificador:
    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _ErrorDeTipo("capacidad debe ser un entero positivo")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise _ErrorDeTipo("dependencias debe ser un diccionario")

        deps = {}
        for nombre, prerrequisitos in list(dependencias.items()):
            _validar_nombre(nombre)
            if isinstance(prerrequisitos, (str, bytes, bytearray)):
                raise _ErrorDeTipo(
                    "los prerrequisitos de %r deben ser un iterable de nombres"
                    % (nombre,)
                )
            try:
                elementos = list(prerrequisitos)
            except TypeError:
                raise _ErrorDeTipo(
                    "los prerrequisitos de %r deben ser un iterable de nombres"
                    % (nombre,)
                ) from None
            for previo in elementos:
                _validar_nombre(previo)
            deps[nombre] = frozenset(elementos)

        for nombre, previos in deps.items():
            for previo in previos:
                if previo not in deps:
                    raise ValueError(
                        "%r depende de una tarea desconocida: %r" % (nombre, previo)
                    )

        self._orden = _orden_topologico(deps)  # también detecta ciclos
        self._deps = deps
        self._capacidad = capacidad
        self._estados = {nombre: PENDIENTE for nombre in sorted(deps)}

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        estados = self._estados
        libres = self._capacidad - sum(1 for e in estados.values() if e == EN_CURSO)
        if libres <= 0:
            return []
        lanzadas = []
        for nombre in sorted(estados):
            if len(lanzadas) >= libres:
                break
            if estados[nombre] == PENDIENTE and all(
                estados[previo] == LISTO for previo in self._deps[nombre]
            ):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        if not isinstance(exito, bool):
            raise _ErrorDeTipo("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("tarea desconocida: %r" % (nombre,))
        if self._estados[nombre] != EN_CURSO:
            raise ValueError("la tarea %r no está en curso" % (nombre,))

        if exito:
            self._estados[nombre] = LISTO
            return None

        self._estados[nombre] = FALLO
        estados = self._estados
        # En orden topológico, los prerrequisitos ya están resueltos al llegar
        # a cada tarea, así que el bloqueo se propaga transitivamente.
        for tarea in self._orden:
            if estados[tarea] == PENDIENTE and any(
                estados[previo] in (FALLO, BLOQUEADO) for previo in self._deps[tarea]
            ):
                estados[tarea] = BLOQUEADO
        return None

    def terminado(self):
        return all(e in _FINALES for e in self._estados.values())


def _validar_nombre(nombre):
    if not isinstance(nombre, str):
        raise _ErrorDeTipo("nombre de tarea inválido: %r" % (nombre,))
    if not nombre:
        raise ValueError("nombre de tarea inválido: %r" % (nombre,))


def _orden_topologico(deps):
    """Prerrequisitos antes que dependientes; ValueError si hay ciclos."""
    BLANCO, GRIS, NEGRO = 0, 1, 2
    color = dict.fromkeys(deps, BLANCO)
    orden = []
    for raiz in sorted(deps):
        if color[raiz] != BLANCO:
            continue
        color[raiz] = GRIS
        pila = [(raiz, iter(sorted(deps[raiz])))]
        while pila:
            nodo, pendientes = pila[-1]
            for previo in pendientes:
                if color[previo] == GRIS:
                    raise ValueError("ciclo de dependencias en %r" % (previo,))
                if color[previo] == BLANCO:
                    color[previo] = GRIS
                    pila.append((previo, iter(sorted(deps[previo]))))
                    break
            else:
                color[nodo] = NEGRO
                orden.append(nodo)
                pila.pop()
    return orden
