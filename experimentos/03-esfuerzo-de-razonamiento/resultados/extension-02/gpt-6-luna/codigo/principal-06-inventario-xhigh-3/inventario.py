"""Libro de inventario con movimientos idempotentes y reversibles."""


class Inventario:
    def __init__(self):
        # Un único reemplazo de este estado publica cada operación completa.
        self._estado = ({}, {}, [], set())

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError("{} debe ser un string no vacío".format(nombre))

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    @staticmethod
    def _validar_id_existente(entradas, identificador, huella):
        existente = entradas.get(identificador)
        if existente is None:
            return False
        if existente[0] != huella:
            raise ValueError("el identificador ya se usó con otros argumentos")
        return True

    def _registrar(self, identificador, huella, registro, saldos, revertidos):
        _, entradas, historial, _ = self._estado
        nuevas_entradas = entradas.copy()
        nuevas_entradas[identificador] = (huella, registro)
        nuevo_historial = historial.copy()
        nuevo_historial.append(registro)
        self._estado = (saldos, nuevas_entradas, nuevo_historial, revertidos)

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "la ubicación")
        saldos, _, _, _ = self._estado
        return saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        huella = ("ingresar", ubicacion, cantidad)

        saldos, entradas, _, revertidos = self._estado
        if self._validar_id_existente(entradas, id, huella):
            return None

        nuevos_saldos = saldos.copy()
        nuevos_saldos[ubicacion] = nuevos_saldos.get(ubicacion, 0) + cantidad
        registro = {
            "id": id,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(id, huella, registro, nuevos_saldos, revertidos)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        huella = ("retirar", ubicacion, cantidad)

        saldos, entradas, _, revertidos = self._estado
        if self._validar_id_existente(entradas, id, huella):
            return None
        if saldos.get(ubicacion, 0) < cantidad:
            raise ValueError("saldo insuficiente")

        nuevos_saldos = saldos.copy()
        nuevos_saldos[ubicacion] -= cantidad
        registro = {
            "id": id,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(id, huella, registro, nuevos_saldos, revertidos)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(origen, "el origen")
        self._validar_texto(destino, "el destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        huella = ("transferir", origen, destino, cantidad)

        saldos, entradas, _, revertidos = self._estado
        if self._validar_id_existente(entradas, id, huella):
            return None
        if saldos.get(origen, 0) < cantidad:
            raise ValueError("saldo insuficiente")

        nuevos_saldos = saldos.copy()
        nuevos_saldos[origen] -= cantidad
        nuevos_saldos[destino] = nuevos_saldos.get(destino, 0) + cantidad
        registro = {
            "id": id,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(id, huella, registro, nuevos_saldos, revertidos)
        return None

    def revertir(self, id, original):
        self._validar_texto(id, "el identificador")
        self._validar_texto(original, "el identificador original")
        huella = ("revertir", original)

        saldos, entradas, _, revertidos = self._estado
        if self._validar_id_existente(entradas, id, huella):
            return None

        entrada_original = entradas.get(original)
        if entrada_original is None:
            raise ValueError("el movimiento original no existe")
        registro_original = entrada_original[1]
        tipo = registro_original["tipo"]
        if tipo == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in revertidos:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = registro_original["cantidad"]
        origen = registro_original["origen"]
        destino = registro_original["destino"]
        nuevos_saldos = saldos.copy()
        if tipo == "ingreso":
            if nuevos_saldos.get(destino, 0) < cantidad:
                raise ValueError("saldo insuficiente para revertir el ingreso")
            nuevos_saldos[destino] -= cantidad
            origen_reversion, destino_reversion = destino, None
        elif tipo == "retiro":
            nuevos_saldos[origen] = nuevos_saldos.get(origen, 0) + cantidad
            origen_reversion, destino_reversion = None, origen
        else:  # transferencia
            if nuevos_saldos.get(destino, 0) < cantidad:
                raise ValueError("saldo insuficiente para revertir la transferencia")
            nuevos_saldos[destino] -= cantidad
            nuevos_saldos[origen] = nuevos_saldos.get(origen, 0) + cantidad
            origen_reversion, destino_reversion = destino, origen

        registro = {
            "id": id,
            "tipo": "reversion",
            "origen": origen_reversion,
            "destino": destino_reversion,
            "cantidad": cantidad,
            "original": original,
        }
        nuevos_revertidos = revertidos.copy()
        nuevos_revertidos.add(original)
        self._registrar(id, huella, registro, nuevos_saldos, nuevos_revertidos)
        return None

    def historial(self):
        _, _, historial, _ = self._estado
        return [registro.copy() for registro in historial]
