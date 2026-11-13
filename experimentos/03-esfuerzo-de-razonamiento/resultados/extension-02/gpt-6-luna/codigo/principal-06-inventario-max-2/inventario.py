class Inventario:
    def __init__(self):
        self._estado = {
            "saldos": {},
            "historial": [],
            "operaciones": {},
            "revertidos": set(),
        }

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "la ubicación")
        return self._estado["saldos"].get(ubicacion, 0)

    def ingresar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        estado = self._estado
        saldos = estado["saldos"].copy()
        saldos[ubicacion] = saldos.get(ubicacion, 0) + cantidad
        movimiento = {
            "id": identificador,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._guardar(estado, saldos, movimiento, identificador, firma)
        return None

    def retirar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        estado = self._estado
        saldo = estado["saldos"].get(ubicacion, 0)
        if saldo < cantidad:
            raise ValueError("saldo insuficiente")
        saldos = estado["saldos"].copy()
        saldos[ubicacion] = saldo - cantidad
        movimiento = {
            "id": identificador,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._guardar(estado, saldos, movimiento, identificador, firma)
        return None

    def transferir(self, identificador, origen, destino, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(origen, "el origen")
        self._validar_texto(destino, "el destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        estado = self._estado
        saldo_origen = estado["saldos"].get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("saldo insuficiente")
        saldos = estado["saldos"].copy()
        saldos[origen] = saldo_origen - cantidad
        saldos[destino] = saldos.get(destino, 0) + cantidad
        movimiento = {
            "id": identificador,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        self._guardar(estado, saldos, movimiento, identificador, firma)
        return None

    def revertir(self, identificador, original):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(original, "el identificador original")
        firma = ("revertir", original)
        if self._es_repeticion(identificador, firma):
            return None

        estado = self._estado
        movimiento_original = self._buscar_movimiento(estado, original)
        if movimiento_original is None:
            raise ValueError("el movimiento original no existe")
        if movimiento_original["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in estado["revertidos"]:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = movimiento_original["cantidad"]
        tipo_original = movimiento_original["tipo"]
        saldos = estado["saldos"].copy()
        if tipo_original == "ingreso":
            ubicacion = movimiento_original["destino"]
            saldo_actual = saldos.get(ubicacion, 0)
            if saldo_actual < cantidad:
                raise ValueError("saldo insuficiente para revertir el ingreso")
            saldos[ubicacion] = saldo_actual - cantidad
        elif tipo_original == "retiro":
            ubicacion = movimiento_original["origen"]
            saldos[ubicacion] = saldos.get(ubicacion, 0) + cantidad
        else:
            origen = movimiento_original["destino"]
            destino = movimiento_original["origen"]
            saldo_origen = saldos.get(origen, 0)
            if saldo_origen < cantidad:
                raise ValueError("saldo insuficiente para revertir la transferencia")
            saldos[origen] = saldo_origen - cantidad
            saldos[destino] = saldos.get(destino, 0) + cantidad

        movimiento = {
            "id": identificador,
            "tipo": "reversion",
            "origen": movimiento_original["destino"],
            "destino": movimiento_original["origen"],
            "cantidad": cantidad,
            "original": original,
        }
        revertidos = estado["revertidos"].copy()
        revertidos.add(original)
        self._guardar(
            estado,
            saldos,
            movimiento,
            identificador,
            firma,
            revertidos=revertidos,
        )
        return None

    def historial(self):
        return [movimiento.copy() for movimiento in self._estado["historial"]]

    def _es_repeticion(self, identificador, firma):
        operaciones = self._estado["operaciones"]
        if identificador not in operaciones:
            return False
        if operaciones[identificador] != firma:
            raise ValueError("el identificador ya fue usado con otros argumentos")
        return True

    @staticmethod
    def _buscar_movimiento(estado, identificador):
        for movimiento in estado["historial"]:
            if movimiento["id"] == identificador:
                return movimiento
        return None

    def _guardar(
        self,
        estado,
        saldos,
        movimiento,
        identificador,
        firma,
        revertidos=None,
    ):
        historial = estado["historial"].copy()
        historial.append(movimiento)
        operaciones = estado["operaciones"].copy()
        operaciones[identificador] = firma
        if revertidos is None:
            revertidos = estado["revertidos"]
        self._estado = {
            "saldos": saldos,
            "historial": historial,
            "operaciones": operaciones,
            "revertidos": revertidos,
        }
