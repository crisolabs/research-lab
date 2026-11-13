"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = []
        self._por_id = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError("Se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _registrar(self, identificador, firma, movimiento, cambios):
        existente = self._por_id.get(identificador)
        if existente is not None:
            if existente["firma"] != firma:
                raise ValueError("El identificador ya se usó con otros argumentos")
            return

        for ubicacion, delta in cambios.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError("Saldo insuficiente")

        for ubicacion, delta in cambios.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta
        self._por_id[identificador] = {"firma": firma, "movimiento": movimiento}
        self._movimientos.append(movimiento)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        movimiento = {"id": id, "tipo": "ingreso", "origen": None,
                      "destino": ubicacion, "cantidad": cantidad, "original": None}
        self._registrar(id, firma, movimiento, {ubicacion: cantidad})

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        movimiento = {"id": id, "tipo": "retiro", "origen": ubicacion,
                      "destino": None, "cantidad": cantidad, "original": None}
        self._registrar(id, firma, movimiento, {ubicacion: -cantidad})

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        movimiento = {"id": id, "tipo": "transferencia", "origen": origen,
                      "destino": destino, "cantidad": cantidad, "original": None}
        self._registrar(id, firma, movimiento, {origen: -cantidad, destino: cantidad})

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)
        existente = self._por_id.get(id)
        if existente is not None:
            if existente["firma"] != firma:
                raise ValueError("El identificador ya se usó con otros argumentos")
            return

        registro = self._por_id.get(original)
        if registro is None:
            raise ValueError("El movimiento original no existe")
        base = registro["movimiento"]
        if base["tipo"] == "reversion" or original in self._revertidos:
            raise ValueError("El movimiento no se puede revertir")

        tipo = base["tipo"]
        if tipo == "ingreso":
            cambios = {base["destino"]: -base["cantidad"]}
        elif tipo == "retiro":
            cambios = {base["origen"]: base["cantidad"]}
        else:
            cambios = {base["origen"]: base["cantidad"],
                       base["destino"]: -base["cantidad"]}

        movimiento = {"id": id, "tipo": "reversion", "origen": base["destino"],
                      "destino": base["origen"], "cantidad": base["cantidad"],
                      "original": original}
        self._registrar(id, firma, movimiento, cambios)
        self._revertidos.add(original)

    def historial(self):
        return [movimiento.copy() for movimiento in self._movimientos]
