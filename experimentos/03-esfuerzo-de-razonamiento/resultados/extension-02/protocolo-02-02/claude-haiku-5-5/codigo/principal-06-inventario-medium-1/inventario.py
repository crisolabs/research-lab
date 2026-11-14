"""Libro de inventario con movimientos idempotentes y reversibles."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        # id -> registro del movimiento (incluye reversiones)
        self._movimientos = {}
        # orden de aplicación
        self._historial = []
        # id original -> id de la reversión que lo revirtió
        self._revertidos = {}

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "ingreso", None, ubicacion, cantidad, None)
        self._aplicar(id, registro, None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "retiro", ubicacion, None, cantidad, None)
        self._aplicar(id, registro, ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "la ubicación de origen")
        _validar_texto(destino, "la ubicación de destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        registro = self._registro(id, "transferencia", origen, destino, cantidad, None)
        self._aplicar(id, registro, origen, destino, cantidad)

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        if original not in self._movimientos:
            raise ValueError("el movimiento original no existe")
        mov = self._movimientos[original]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            # Si la misma reversión ya existe, _registro la detecta como repetición.
            if self._revertidos[original] != id:
                raise ValueError("el movimiento ya fue revertido")
        registro = self._registro(
            id, "reversion", mov["destino"], mov["origen"], mov["cantidad"], original
        )
        if id in self._movimientos:
            return  # repetición idéntica: no hace nada
        self._aplicar(id, registro, mov["destino"], mov["origen"], mov["cantidad"])
        self._revertidos[original] = id

    def historial(self):
        return [dict(r) for r in self._historial]

    # --- internos ---

    def _registro(self, id, tipo, origen, destino, cantidad, original):
        """Devuelve el registro propuesto; si el id ya existe, valida que coincida."""
        propuesto = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        if id in self._movimientos:
            if self._movimientos[id] == propuesto:
                return propuesto
            raise ValueError("identificador reutilizado con argumentos distintos")
        return propuesto

    def _aplicar(self, id, registro, origen, destino, cantidad):
        """Valida y aplica un movimiento nuevo. Ante error no modifica nada."""
        if id in self._movimientos:
            # Repetición idéntica (validada en _registro): no hace nada.
            return
        if origen is not None and self._saldos.get(origen, 0) < cantidad:
            raise ValueError("saldo insuficiente")
        if origen is not None:
            self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._movimientos[id] = dict(registro)
        self._historial.append(dict(registro))
