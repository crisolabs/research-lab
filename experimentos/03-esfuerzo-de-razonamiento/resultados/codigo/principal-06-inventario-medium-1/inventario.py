class Inventario:
    def __init__(self):
        self._estado = ({}, [], {}, set())

    @staticmethod
    def _validar_string(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_string(ubicacion)
        return self._estado[0].get(ubicacion, 0)

    def _repetido(self, id, argumentos):
        solicitudes = self._estado[2]
        if id not in solicitudes:
            return False
        if solicitudes[id] != argumentos:
            raise ValueError("El identificador ya tiene otros argumentos")
        return True

    def _guardar(self, movimiento, argumentos, variaciones):
        saldos, historial, solicitudes, revertidos = self._estado
        nuevos_saldos = saldos.copy()
        for ubicacion, variacion in variaciones:
            nuevo_saldo = nuevos_saldos.get(ubicacion, 0) + variacion
            if nuevo_saldo < 0:
                raise ValueError("Saldo insuficiente")
            nuevos_saldos[ubicacion] = nuevo_saldo
        nuevo_historial = historial + [movimiento]
        nuevas_solicitudes = solicitudes.copy()
        nuevas_solicitudes[movimiento["id"]] = argumentos
        nuevos_revertidos = revertidos.copy()
        if movimiento["tipo"] == "reversion":
            nuevos_revertidos.add(movimiento["original"])
        self._estado = (
            nuevos_saldos, nuevo_historial, nuevas_solicitudes, nuevos_revertidos
        )

    def _mover(self, id, tipo, origen, destino, cantidad):
        self._validar_string(id)
        if origen is not None:
            self._validar_string(origen)
        if destino is not None:
            self._validar_string(destino)
        self._validar_cantidad(cantidad)
        if tipo == "transferencia" and origen == destino:
            raise ValueError("Origen y destino deben ser distintos")
        argumentos = (tipo, origen, destino, cantidad)
        if self._repetido(id, argumentos):
            return
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        self._guardar(
            dict(id=id, tipo=tipo, origen=origen, destino=destino,
                 cantidad=cantidad, original=None),
            argumentos,
            variaciones,
        )

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_string(ubicacion)
        self._mover(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_string(ubicacion)
        self._mover(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_string(origen)
        self._validar_string(destino)
        self._mover(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._validar_string(id)
        self._validar_string(original)
        argumentos = ("reversion", original)
        if self._repetido(id, argumentos):
            return
        _, historial, solicitudes, revertidos = self._estado
        if original not in solicitudes or original in revertidos:
            raise ValueError("El movimiento no existe o ya fue revertido")
        movimiento = next(m for m in historial if m["id"] == original)
        if movimiento["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        origen = movimiento["destino"]
        destino = movimiento["origen"]
        cantidad = movimiento["cantidad"]
        variaciones = []
        if origen is not None:
            variaciones.append((origen, -cantidad))
        if destino is not None:
            variaciones.append((destino, cantidad))
        self._guardar(
            dict(id=id, tipo="reversion", origen=origen, destino=destino,
                 cantidad=cantidad, original=original),
            argumentos,
            variaciones,
        )

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado[1]]
