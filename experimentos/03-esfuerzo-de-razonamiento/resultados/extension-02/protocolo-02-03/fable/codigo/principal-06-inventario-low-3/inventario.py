"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro (dict), en orden de aplicación
        self._revertidos = set()  # ids de movimientos ya revertidos

    # ------------------------------------------------------------------ consultas
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(m) for m in self._movimientos.values()]

    # ------------------------------------------------------------------ mutaciones
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._registrar(self._registro(id, "ingreso", None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._registrar(self._registro(id, "retiro", ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._registrar(
            self._registro(id, "transferencia", origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        previo = self._movimientos.get(id)
        if previo is not None:
            if previo["tipo"] == "reversion" and previo["original"] == original:
                return None
            raise ValueError("identificador reutilizado con argumentos distintos")
        mov = self._movimientos.get(original)
        if mov is None:
            raise ValueError("el movimiento original no existe")
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")
        self._registrar(
            self._registro(
                id, "reversion", mov["destino"], mov["origen"], mov["cantidad"], original
            )
        )
        self._revertidos.add(original)

    # ------------------------------------------------------------------ internos
    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original):
        # Se normalizan a tipos base para que el libro no dependa de subclases
        # (posiblemente mutables o con igualdad propia) aportadas por el llamador.
        return {
            "id": str(id),
            "tipo": tipo,
            "origen": None if origen is None else str(origen),
            "destino": None if destino is None else str(destino),
            "cantidad": int(cantidad),
            "original": None if original is None else str(original),
        }

    def _registrar(self, reg):
        """Aplica el registro de forma atómica, o no hace nada si es repetido."""
        previo = self._movimientos.get(reg["id"])
        if previo is not None:
            if previo == reg:
                return
            raise ValueError("identificador reutilizado con argumentos distintos")
        origen, destino, cantidad = reg["origen"], reg["destino"], reg["cantidad"]
        if origen is not None and self._saldos.get(origen, 0) < cantidad:
            raise ValueError("saldo insuficiente")
        # A partir de acá nada puede fallar.
        if origen is not None:
            self._saldos[origen] -= cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._movimientos[reg["id"]] = reg
