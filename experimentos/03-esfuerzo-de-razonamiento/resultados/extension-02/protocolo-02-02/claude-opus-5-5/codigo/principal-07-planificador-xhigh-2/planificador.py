"""Planificador de dependencias: administra los estados de tareas con prerrequisitos.

El módulo no ejecuta nada: sólo decide qué tareas pueden lanzarse y registra
sus resultados.
"""

from collections.abc import Mapping

__all__ = ["Planificador"]

PENDIENTE = "pendiente"
EN_CURSO = "en_curso"
LISTO = "listo"
FALLO = "fallo"
BLOQUEADO = "bloqueado"

_TERMINALES = frozenset((LISTO, FALLO, BLOQUEADO))


class _ErrorDeTipo(ValueError, TypeError):
    """Error de validación por tipo incorrecto.

    Es un ``ValueError`` (lo que exige el enunciado) y además un ``TypeError``.
    """


def _normalizar_nombre(nombre, que):
    """Valida que ``nombre`` sea un string no vacío y lo devuelve como ``str`` puro."""
    if not isinstance(nombre, str):
        raise _ErrorDeTipo(
            f"{que} debe ser un string no vacío, no {type(nombre).__name__}"
        )
    # Copia como str exacto: evita subclases con __eq__/__hash__ alterados.
    nombre = str.__str__(nombre)
    if not nombre:
        raise ValueError(f"{que} no puede ser un string vacío")
    return nombre


class Planificador:
    """Planifica tareas respetando dependencias y un límite de tareas en curso."""

    def __init__(self, dependencias, capacidad):
        # --- capacidad ---------------------------------------------------
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise _ErrorDeTipo("capacidad debe ser un entero positivo (no booleano)")
        capacidad = int(capacidad)
        if capacidad <= 0:
            raise ValueError(f"capacidad debe ser positiva, se recibió {capacidad}")

        # --- dependencias: copia y validación de nombres ----------------
        if not isinstance(dependencias, Mapping):
            raise _ErrorDeTipo("dependencias debe ser un diccionario")
        entradas = list(dependencias.items())

        claves = []
        nombres = set()
        for clave, _ in entradas:
            nombre = _normalizar_nombre(clave, "el nombre de una tarea")
            if nombre in nombres:
                raise ValueError(f"tarea duplicada: {nombre!r}")
            nombres.add(nombre)
            claves.append(nombre)

        prerrequisitos = {}
        for nombre, (_, valor) in zip(claves, entradas):
            if isinstance(valor, (str, bytes, bytearray)):
                raise _ErrorDeTipo(
                    f"los prerrequisitos de {nombre!r} deben ser un iterable de "
                    "nombres, no un string"
                )
            try:
                iterador = iter(valor)
            except TypeError:
                raise _ErrorDeTipo(
                    f"los prerrequisitos de {nombre!r} deben ser iterables"
                ) from None
            requeridos = set()
            for prerrequisito in iterador:
                prerrequisito = _normalizar_nombre(
                    prerrequisito, f"un prerrequisito de {nombre!r}"
                )
                if prerrequisito not in nombres:
                    raise ValueError(
                        f"{nombre!r} depende de una tarea desconocida: "
                        f"{prerrequisito!r}"
                    )
                requeridos.add(prerrequisito)
            prerrequisitos[nombre] = frozenset(requeridos)

        orden = tuple(sorted(nombres))

        dependientes = {nombre: [] for nombre in orden}
        for nombre in orden:
            for prerrequisito in prerrequisitos[nombre]:
                dependientes[prerrequisito].append(nombre)
        dependientes = {n: tuple(sorted(ds)) for n, ds in dependientes.items()}

        # --- detección de ciclos (Kahn; incluye auto dependencia) --------
        faltantes = {nombre: len(prerrequisitos[nombre]) for nombre in orden}
        cola = [nombre for nombre in orden if faltantes[nombre] == 0]
        procesadas = 0
        while cola:
            actual = cola.pop()
            procesadas += 1
            for dependiente in dependientes[actual]:
                faltantes[dependiente] -= 1
                if faltantes[dependiente] == 0:
                    cola.append(dependiente)
        if procesadas != len(orden):
            involucradas = ", ".join(
                repr(nombre) for nombre in orden if faltantes[nombre] > 0
            )
            raise ValueError(f"ciclo de dependencias entre: {involucradas}")

        # --- estado interno (sólo se asigna si todo es válido) ----------
        self._capacidad = capacidad
        self._orden = orden
        self._prerrequisitos = {nombre: prerrequisitos[nombre] for nombre in orden}
        self._dependientes = dependientes
        self._estados = {nombre: PENDIENTE for nombre in orden}

    def estados(self):
        """Devuelve una copia del diccionario nombre → estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza (marca ``en_curso``) tareas habilitadas hasta llenar la capacidad.

        Devuelve la lista de tareas nuevas, en orden lexicográfico.
        """
        en_curso = sum(1 for estado in self._estados.values() if estado == EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in self._orden:
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != PENDIENTE:
                continue
            if all(self._estados[p] == LISTO for p in self._prerrequisitos[nombre]):
                lanzadas.append(nombre)
        for nombre in lanzadas:
            self._estados[nombre] = EN_CURSO
        return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea ``en_curso``.

        Con éxito la marca ``listo``; si falla la marca ``fallo`` y bloquea
        toda tarea pendiente que dependa de ella directa o transitivamente.
        """
        if not isinstance(exito, bool):
            raise _ErrorDeTipo("exito debe ser un booleano")
        if not isinstance(nombre, str):
            raise _ErrorDeTipo(f"tarea desconocida: {type(nombre).__name__}")
        nombre = str.__str__(nombre)
        estado = self._estados.get(nombre)
        if estado is None:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if estado != EN_CURSO:
            raise ValueError(
                f"la tarea {nombre!r} no está en curso (estado: {estado})"
            )

        if exito:
            self._estados[nombre] = LISTO
            return None

        # Calcular primero todo lo que hay que bloquear y luego aplicar.
        a_bloquear = []
        visitadas = set(self._dependientes[nombre])
        pila = list(self._dependientes[nombre])
        while pila:
            actual = pila.pop()
            if self._estados[actual] == PENDIENTE:
                a_bloquear.append(actual)
            for dependiente in self._dependientes[actual]:
                if dependiente not in visitadas:
                    visitadas.add(dependiente)
                    pila.append(dependiente)

        self._estados[nombre] = FALLO
        for bloqueada in a_bloquear:
            self._estados[bloqueada] = BLOQUEADO
        return None

    def terminado(self):
        """Indica si todas las tareas están ``listo``, ``fallo`` o ``bloqueado``."""
        return all(estado in _TERMINALES for estado in self._estados.values())
