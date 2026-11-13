class Inventario:
    def __init__(self):
        self._saldos = {}
        self._operaciones = {}
        self._historial = []
        self._revertidos = set()

    @staticmethod
    def _texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("texto inválido")

    @staticmethod
    def _cantidad(valor):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError("cantidad inválida")

    def saldo(self, ubicacion):
        self._texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(movimiento) for movimiento in self._historial]

    def _repetido(self, identificador, firma):
        self._texto(identificador)
        if identificador in self._operaciones:
            if self._operaciones[identificador] != firma:
                raise ValueError("identificador reutilizado")
            return True
        return False

    def _aplicar(self, identificador, firma, tipo, origen, destino, cantidad, original=None):
        cambios = {}
        if origen is not None:
            cambios[origen] = cambios.get(origen, 0) - cantidad
        if destino is not None:
            cambios[destino] = cambios.get(destino, 0) + cantidad
        nuevos = {lugar: self._saldos.get(lugar, 0) + cambio for lugar, cambio in cambios.items()}
        if any(saldo < 0 for saldo in nuevos.values()):
            raise ValueError("saldo insuficiente")
        self._saldos.update(nuevos)
        self._operaciones[identificador] = firma
        self._historial.append(dict(id=identificador, tipo=tipo, origen=origen, destino=destino, cantidad=cantidad, original=original))

    def ingresar(self, id, ubicacion, cantidad):
        self._texto(ubicacion)
        self._cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, firma):
            return
        self._aplicar(id, firma, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._texto(ubicacion)
        self._cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._repetido(id, firma):
            return
        self._aplicar(id, firma, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._texto(origen)
        self._texto(destino)
        self._cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino iguales")
        firma = ("transferencia", origen, destino, cantidad)
        if self._repetido(id, firma):
            return
        self._aplicar(id, firma, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        self._texto(original)
        firma = ("reversion", original)
        if self._repetido(id, firma):
            return
        registros = {m["id"]: m for m in self._historial}
        if original not in registros or original in self._revertidos:
            raise ValueError("original inválido")
        movimiento = registros[original]
        if movimiento["tipo"] == "reversion":
            raise ValueError("no se revierte una reversión")
        self._aplicar(id, firma, "reversion", movimiento["destino"], movimiento["origen"], movimiento["cantidad"], original)
        self._revertidos.add(original)
