class Planificador:
    TERMINALES = {"listo", "fallo", "bloqueado"}

    def __init__(self, dependencias, capacidad):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ValueError("capacidad inválida")
        if any(not isinstance(n, str) or not n for n in dependencias):
            raise ValueError("nombre inválido")
        self._deps = {}
        for nombre, requisitos in dependencias.items():
            elementos = list(requisitos)
            if any(not isinstance(n, str) or not n for n in elementos):
                raise ValueError("dependencia inválida")
            valores = set(elementos)
            if not valores.issubset(dependencias):
                raise ValueError("referencia desconocida")
            self._deps[nombre] = valores
        self._validar_ciclos()
        self._capacidad = capacidad
        self._estados = {n: "pendiente" for n in self._deps}

    def _validar_ciclos(self):
        restantes = {n: set(ds) for n, ds in self._deps.items()}
        procesadas = set()
        while restantes:
            habilitadas = {n for n, ds in restantes.items() if ds <= procesadas}
            if not habilitadas:
                raise ValueError("ciclo")
            procesadas.update(habilitadas)
            for nombre in habilitadas:
                del restantes[nombre]

    def estados(self):
        return dict(self._estados)

    def tomar(self):
        activas = sum(s == "en_curso" for s in self._estados.values())
        disponibles = self._capacidad - activas
        elegidas = []
        for nombre in sorted(self._deps):
            if len(elegidas) >= disponibles:
                break
            if self._estados[nombre] != "pendiente":
                continue
            if all(self._estados[d] == "listo" for d in self._deps[nombre]):
                elegidas.append(nombre)
        for nombre in elegidas:
            self._estados[nombre] = "en_curso"
        return elegidas

    def completar(self, nombre, exito=True):
        if not isinstance(nombre, str) or nombre not in self._estados:
            raise ValueError("nombre desconocido")
        if not isinstance(exito, bool):
            raise ValueError("éxito inválido")
        if self._estados[nombre] != "en_curso":
            raise ValueError("tarea no activa")
        self._estados[nombre] = "listo" if exito else "fallo"
        self._propagar_bloqueos()

    def _propagar_bloqueos(self):
        cambio = True
        while cambio:
            cambio = False
            for nombre, requisitos in self._deps.items():
                if self._estados[nombre] != "pendiente":
                    continue
                if any(self._estados[d] in {"fallo", "bloqueado"} for d in requisitos):
                    self._estados[nombre] = "bloqueado"
                    cambio = True

    def terminado(self):
        return all(s in self.TERMINALES for s in self._estados.values())
