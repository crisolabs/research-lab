"""Planificador de tareas con dependencias, según TAREA.md."""

_PENDIENTE = "pendiente"
_EN_CURSO = "en_curso"
_LISTO = "listo"
_FALLO = "fallo"
_BLOQUEADO = "bloqueado"
_TERMINALES = frozenset({_LISTO, _FALLO, _BLOQUEADO})


def _validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre:
        raise ValueError(f"nombre inválido: {nombre!r}")
    return nombre


class Planificador:
    """Administra estados de tareas con dependencias; no ejecuta nada."""

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad debe ser un entero positivo")
        if not isinstance(dependencias, dict):
            raise ValueError("dependencias debe ser un diccionario")

        # Copia interna: nombre -> frozenset de prerrequisitos (sin repetidos).
        prereqs = {}
        for nombre, requisitos in dependencias.items():
            _validar_nombre(nombre)
            if isinstance(requisitos, (str, bytes)) or not hasattr(requisitos, "__iter__"):
                raise ValueError(f"dependencias inválidas para {nombre!r}")
            prereqs[nombre] = frozenset(_validar_nombre(r) for r in requisitos)

        for nombre, req in prereqs.items():
            for r in req:
                if r not in prereqs:
                    raise ValueError(f"referencia desconocida: {r!r} en {nombre!r}")

        self._capacidad = capacidad
        self._prereqs = prereqs
        self._dependientes = {n: set() for n in prereqs}
        for nombre, req in prereqs.items():
            for r in req:
                self._dependientes[r].add(nombre)

        self._verificar_aciclico()
        self._estados = {n: _PENDIENTE for n in prereqs}

    def _verificar_aciclico(self):
        # Algoritmo de Kahn: si no se pueden ordenar todos los nodos, hay ciclo.
        grados = {n: len(req) for n, req in self._prereqs.items()}
        cola = [n for n, g in grados.items() if g == 0]
        procesados = 0
        while cola:
            n = cola.pop()
            procesados += 1
            for d in self._dependientes[n]:
                grados[d] -= 1
                if grados[d] == 0:
                    cola.append(d)
        if procesados != len(self._prereqs):
            raise ValueError("el grafo contiene ciclos")

    def estados(self):
        """Devuelve una copia del diccionario nombre -> estado."""
        return dict(self._estados)

    def tomar(self):
        """Lanza nuevas tareas habilitadas hasta llenar la capacidad."""
        en_curso = sum(1 for e in self._estados.values() if e == _EN_CURSO)
        libres = self._capacidad - en_curso
        lanzadas = []
        if libres <= 0:
            return lanzadas
        for nombre in sorted(self._estados):
            if len(lanzadas) >= libres:
                break
            if self._estados[nombre] != _PENDIENTE:
                continue
            if all(self._estados[r] == _LISTO for r in self._prereqs[nombre]):
                self._estados[nombre] = _EN_CURSO
                lanzadas.append(nombre)
        return lanzadas

    def completar(self, nombre, exito=True):
        """Registra el resultado de una tarea en curso."""
        if not isinstance(exito, bool):
            raise ValueError("exito debe ser bool")
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError(f"tarea desconocida: {nombre!r}")
        if self._estados[nombre] != _EN_CURSO:
            raise ValueError(f"la tarea {nombre!r} no está en curso")

        if exito:
            self._estados[nombre] = _LISTO
            return None

        self._estados[nombre] = _FALLO
        pila = list(self._dependientes[nombre])
        while pila:
            n = pila.pop()
            if self._estados[n] != _PENDIENTE:
                continue
            self._estados[n] = _BLOQUEADO
            pila.extend(self._dependientes[n])
        return None

    def terminado(self):
        """True si todas las tareas están en un estado terminal."""
        return all(e in _TERMINALES for e in self._estados.values())
