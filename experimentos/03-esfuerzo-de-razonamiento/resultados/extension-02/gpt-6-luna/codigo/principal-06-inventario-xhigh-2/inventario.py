class Inventario:
    def __init__(self):
        self._state = ({}, {}, {}, [], set())

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or not valor:
            raise ValueError("{} debe ser un string no vacío".format(nombre))

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "la ubicación")
        return self._state[0].get(ubicacion, 0)

    def _es_repeticion(self, identificador, firma):
        firmas = self._state[1]
        if identificador not in firmas:
            return False
        if firmas[identificador] != firma:
            raise ValueError("el identificador ya se usó con otra operación")
        return True

    def ingresar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        balances, firmas, registros, historial, reversiones = self._state
        nuevos_balances = balances.copy()
        nuevos_balances[ubicacion] = balances.get(ubicacion, 0) + cantidad
        nuevos_firmas = firmas.copy()
        nuevos_firmas[identificador] = firma
        registro = {
            "id": identificador,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        nuevos_registros = registros.copy()
        nuevos_registros[identificador] = registro
        nuevo_historial = historial + [registro]
        self._state = (nuevos_balances, nuevos_firmas, nuevos_registros,
                       nuevo_historial, reversiones)
        return None

    def retirar(self, identificador, ubicacion, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        balances, firmas, registros, historial, reversiones = self._state
        disponible = balances.get(ubicacion, 0)
        if disponible < cantidad:
            raise ValueError("saldo insuficiente")

        nuevos_balances = balances.copy()
        nuevos_balances[ubicacion] = disponible - cantidad
        nuevos_firmas = firmas.copy()
        nuevos_firmas[identificador] = firma
        registro = {
            "id": identificador,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        nuevos_registros = registros.copy()
        nuevos_registros[identificador] = registro
        nuevo_historial = historial + [registro]
        self._state = (nuevos_balances, nuevos_firmas, nuevos_registros,
                       nuevo_historial, reversiones)
        return None

    def transferir(self, identificador, origen, destino, cantidad):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(origen, "la ubicación de origen")
        self._validar_texto(destino, "la ubicación de destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._es_repeticion(identificador, firma):
            return None

        balances, firmas, registros, historial, reversiones = self._state
        disponible = balances.get(origen, 0)
        if disponible < cantidad:
            raise ValueError("saldo insuficiente")

        nuevos_balances = balances.copy()
        nuevos_balances[origen] = disponible - cantidad
        nuevos_balances[destino] = balances.get(destino, 0) + cantidad
        nuevos_firmas = firmas.copy()
        nuevos_firmas[identificador] = firma
        registro = {
            "id": identificador,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        nuevos_registros = registros.copy()
        nuevos_registros[identificador] = registro
        nuevo_historial = historial + [registro]
        self._state = (nuevos_balances, nuevos_firmas, nuevos_registros,
                       nuevo_historial, reversiones)
        return None

    def revertir(self, identificador, original):
        self._validar_texto(identificador, "el identificador")
        self._validar_texto(original, "el identificador original")
        firma = ("reversion", original)
        if self._es_repeticion(identificador, firma):
            return None

        balances, firmas, registros, historial, reversiones = self._state
        if original not in registros:
            raise ValueError("el movimiento original no existe")
        movimiento = registros[original]
        if movimiento["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in reversiones:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = movimiento["cantidad"]
        cambios = {}
        if movimiento["tipo"] == "ingreso":
            cambios[movimiento["destino"]] = -cantidad
        elif movimiento["tipo"] == "retiro":
            cambios[movimiento["origen"]] = cantidad
        else:
            cambios[movimiento["destino"]] = -cantidad
            cambios[movimiento["origen"]] = cantidad

        for ubicacion, cambio in cambios.items():
            if balances.get(ubicacion, 0) + cambio < 0:
                raise ValueError("saldo insuficiente para revertir")

        nuevos_balances = balances.copy()
        for ubicacion, cambio in cambios.items():
            nuevos_balances[ubicacion] = balances.get(ubicacion, 0) + cambio
        nuevos_firmas = firmas.copy()
        nuevos_firmas[identificador] = firma
        registro = {
            "id": identificador,
            "tipo": "reversion",
            "origen": movimiento["destino"],
            "destino": movimiento["origen"],
            "cantidad": cantidad,
            "original": original,
        }
        nuevos_registros = registros.copy()
        nuevos_registros[identificador] = registro
        nuevo_historial = historial + [registro]
        nuevas_reversiones = reversiones.copy()
        nuevas_reversiones.add(original)
        self._state = (nuevos_balances, nuevos_firmas, nuevos_registros,
                       nuevo_historial, nuevas_reversiones)
        return None

    def historial(self):
        return [registro.copy() for registro in self._state[3]]
