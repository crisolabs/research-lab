class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._operaciones = {}
        self._revertidos = set()

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
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_string(ubicacion)
        self._mover(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        self._validar_string(ubicacion)
        self._mover(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        self._validar_string(origen)
        self._validar_string(destino)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        self._mover(id, "transferencia", origen, destino, cantidad)

    def _mover(self, id, tipo, origen, destino, cantidad):
        self._validar_string(id)
        if origen is not None:
            self._validar_string(origen)
        if destino is not None:
            self._validar_string(destino)
        self._validar_cantidad(cantidad)
        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        if self._es_repeticion(id, registro):
            return
        self._aplicar(registro)

    def _es_repeticion(self, id, registro):
        if id not in self._operaciones:
            return False
        if self._operaciones[id] != registro:
            raise ValueError("El identificador ya pertenece a otra operación")
        return True

    def _aplicar(self, registro):
        saldos = self._saldos.copy()
        origen = registro["origen"]
        destino = registro["destino"]
        cantidad = registro["cantidad"]
        if origen is not None:
            if saldos.get(origen, 0) < cantidad:
                raise ValueError("Saldo insuficiente")
            saldos[origen] = saldos.get(origen, 0) - cantidad
        if destino is not None:
            saldos[destino] = saldos.get(destino, 0) + cantidad
        historial = self._historial + [registro]
        operaciones = self._operaciones.copy()
        operaciones[registro["id"]] = registro
        revertidos = self._revertidos.copy()
        if registro["tipo"] == "reversion":
            revertidos.add(registro["original"])
        self._saldos = saldos
        self._historial = historial
        self._operaciones = operaciones
        self._revertidos = revertidos

    def revertir(self, id, original):
        self._validar_string(id)
        self._validar_string(original)
        movimiento = self._operaciones.get(original)
        if movimiento is None or movimiento["tipo"] == "reversion":
            raise ValueError("El movimiento original no se puede revertir")
        registro = {
            "id": id,
            "tipo": "reversion",
            "origen": movimiento["destino"],
            "destino": movimiento["origen"],
            "cantidad": movimiento["cantidad"],
            "original": original,
        }
        if self._es_repeticion(id, registro):
            return
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")
        self._aplicar(registro)

    def historial(self):
        return [registro.copy() for registro in self._historial]
