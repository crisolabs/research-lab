"""Libro de inventario con movimientos idempotentes y reversiones."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> firma de la operación (para idempotencia)
        self._firmas = {}
        # id -> índice en el historial
        self._indices = {}
        # ids de movimientos ya revertidos
        self._revertidos = set()

    # ------------------------------------------------------------------
    # Validaciones
    @staticmethod
    def _validar_texto(valor):
        if not isinstance(valor, str) or valor == "":
            raise ValueError("se requiere un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            raise ValueError("la cantidad debe ser un entero positivo")

    def _ya_aplicado(self, id_, firma):
        """Devuelve True si el id ya se aplicó con la misma firma.

        Lanza ValueError si el id existe con otra firma.
        """
        existente = self._firmas.get(id_)
        if existente is None:
            return False
        if existente == firma:
            return True
        raise ValueError("identificador reutilizado con argumentos distintos")

    def _registrar(self, id_, firma, tipo, origen, destino, cantidad, original):
        self._firmas[id_] = firma
        self._indices[id_] = len(self._historial)
        self._historial.append(
            {
                "id": id_,
                "tipo": tipo,
                "origen": origen,
                "destino": destino,
                "cantidad": cantidad,
                "original": original,
            }
        )

    # ------------------------------------------------------------------
    # Consultas
    def saldo(self, ubicacion):
        self._validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(mov) for mov in self._historial]

    # ------------------------------------------------------------------
    # Mutaciones
    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
        self._registrar(id, firma, "ingreso", None, ubicacion, cantidad, None)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id)
        self._validar_texto(ubicacion)
        self._validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        actual = self._saldos.get(ubicacion, 0)
        if actual < cantidad:
            raise ValueError("saldo insuficiente")
        self._saldos[ubicacion] = actual - cantidad
        self._registrar(id, firma, "retiro", ubicacion, None, cantidad, None)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id)
        self._validar_texto(origen)
        self._validar_texto(destino)
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        saldo_origen = self._saldos.get(origen, 0)
        if saldo_origen < cantidad:
            raise ValueError("saldo insuficiente")
        saldo_destino = self._saldos.get(destino, 0)
        self._saldos[origen] = saldo_origen - cantidad
        self._saldos[destino] = saldo_destino + cantidad
        self._registrar(
            id, firma, "transferencia", origen, destino, cantidad, None
        )
        return None

    def revertir(self, id, original):
        self._validar_texto(id)
        self._validar_texto(original)
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        indice = self._indices.get(original)
        if indice is None:
            raise ValueError("movimiento original inexistente")
        mov = self._historial[indice]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = mov["cantidad"]
        # Variaciones a deshacer: el destino original pierde, el origen gana.
        variaciones = {}
        if mov["destino"] is not None:
            variaciones[mov["destino"]] = variaciones.get(mov["destino"], 0) - cantidad
        if mov["origen"] is not None:
            variaciones[mov["origen"]] = variaciones.get(mov["origen"], 0) + cantidad

        nuevos = {}
        for ubicacion, delta in variaciones.items():
            nuevo = self._saldos.get(ubicacion, 0) + delta
            if nuevo < 0:
                raise ValueError("la reversión dejaría un saldo negativo")
            nuevos[ubicacion] = nuevo

        self._saldos.update(nuevos)
        self._revertidos.add(original)
        self._registrar(
            id,
            firma,
            "reversion",
            mov["destino"],
            mov["origen"],
            cantidad,
            original,
        )
        return None
