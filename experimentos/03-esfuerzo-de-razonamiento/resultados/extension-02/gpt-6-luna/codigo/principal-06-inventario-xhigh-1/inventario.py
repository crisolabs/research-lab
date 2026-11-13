"""Libro de movimientos de inventario."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        # Cada identificador guarda la firma de la llamada y su entrada.
        self._por_id = {}
        self._revertidos = set()

    @staticmethod
    def _validar_texto(nombre, valor):
        if not isinstance(valor, str) or not valor:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero positivo")

    def _ya_aplicado(self, identificador, firma):
        existente = self._por_id.get(identificador)
        if existente is None:
            return False
        if existente[0] != firma:
            raise ValueError("El identificador ya se usó con otra operación")
        return True

    def _registrar(self, identificador, firma, entrada, cambios, original_revertido=None):
        # Preparar todos los cambios antes de reemplazar el estado evita dejar
        # una operación aplicada a medias si falla su preparación.
        saldos = self._saldos.copy()
        saldos.update(cambios)
        historial = self._historial.copy()
        historial.append(entrada)
        por_id = self._por_id.copy()
        por_id[identificador] = (firma, entrada)
        revertidos = self._revertidos.copy()
        if original_revertido is not None:
            revertidos.add(original_revertido)

        self._saldos, self._historial, self._por_id, self._revertidos = (
            saldos,
            historial,
            por_id,
            revertidos,
        )

    def saldo(self, ubicacion):
        self._validar_texto("La ubicación", ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, identificador, ubicacion, cantidad):
        self._validar_texto("El identificador", identificador)
        self._validar_texto("La ubicación", ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._ya_aplicado(identificador, firma):
            return None

        entrada = {
            "id": identificador,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        }
        nuevo_saldo = self._saldos.get(ubicacion, 0) + cantidad
        self._registrar(identificador, firma, entrada, {ubicacion: nuevo_saldo})
        return None

    def retirar(self, identificador, ubicacion, cantidad):
        self._validar_texto("El identificador", identificador)
        self._validar_texto("La ubicación", ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._ya_aplicado(identificador, firma):
            return None

        saldo_actual = self._saldos.get(ubicacion, 0)
        if saldo_actual < cantidad:
            raise ValueError("Saldo insuficiente")
        entrada = {
            "id": identificador,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        }
        self._registrar(
            identificador,
            firma,
            entrada,
            {ubicacion: saldo_actual - cantidad},
        )
        return None

    def transferir(self, identificador, origen, destino, cantidad):
        self._validar_texto("El identificador", identificador)
        self._validar_texto("El origen", origen)
        self._validar_texto("El destino", destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if self._ya_aplicado(identificador, firma):
            return None

        saldo_origen = self._saldos.get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("Saldo insuficiente")
        entrada = {
            "id": identificador,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        }
        cambios = {
            origen: saldo_origen - cantidad,
            destino: self._saldos.get(destino, 0) + cantidad,
        }
        self._registrar(identificador, firma, entrada, cambios)
        return None

    def revertir(self, identificador, original):
        self._validar_texto("El identificador", identificador)
        self._validar_texto("El movimiento original", original)
        firma = ("revertir", original)
        if self._ya_aplicado(identificador, firma):
            return None

        movimiento = self._por_id.get(original)
        if movimiento is None:
            raise ValueError("El movimiento original no existe")
        entrada_original = movimiento[1]
        tipo = entrada_original["tipo"]
        if tipo == "reversion":
            raise ValueError("No se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("El movimiento ya fue revertido")

        cantidad = entrada_original["cantidad"]
        origen_original = entrada_original["origen"]
        destino_original = entrada_original["destino"]
        entrada = {
            "id": identificador,
            "tipo": "reversion",
            "origen": destino_original,
            "destino": origen_original,
            "cantidad": cantidad,
            "original": original,
        }

        if tipo == "ingreso":
            ubicacion = destino_original
            saldo_actual = self._saldos.get(ubicacion, 0)
            if saldo_actual < cantidad:
                raise ValueError("La reversión dejaría un saldo negativo")
            cambios = {ubicacion: saldo_actual - cantidad}
        elif tipo == "retiro":
            cambios = {
                origen_original: self._saldos.get(origen_original, 0) + cantidad
            }
        else:  # transferencia
            saldo_destino = self._saldos.get(destino_original, 0)
            if saldo_destino < cantidad:
                raise ValueError("La reversión dejaría un saldo negativo")
            cambios = {
                origen_original: self._saldos.get(origen_original, 0) + cantidad,
                destino_original: saldo_destino - cantidad,
            }

        self._registrar(
            identificador,
            firma,
            entrada,
            cambios,
            original_revertido=original,
        )
        return None

    def historial(self):
        return [entrada.copy() for entrada in self._historial]
