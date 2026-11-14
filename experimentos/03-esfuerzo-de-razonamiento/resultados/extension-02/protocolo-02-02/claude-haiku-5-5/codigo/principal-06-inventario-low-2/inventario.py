"""Libro de inventario con movimientos idempotentes y reversibles."""


def _texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


def _efecto(movimiento):
    """Devuelve los deltas de saldo que produce un movimiento."""
    tipo = movimiento["tipo"]
    cantidad = movimiento["cantidad"]
    if tipo == "ingreso":
        return {movimiento["destino"]: cantidad}
    if tipo == "retiro":
        return {movimiento["origen"]: -cantidad}
    # transferencia y reversion: resta del origen, suma al destino
    deltas = {}
    deltas[movimiento["origen"]] = deltas.get(movimiento["origen"], 0) - cantidad
    deltas[movimiento["destino"]] = deltas.get(movimiento["destino"], 0) + cantidad
    return deltas


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._indice = {}      # id -> movimiento (interno)
        self._historial = []   # movimientos en orden de aplicación (interno)
        self._revertidos = set()  # ids de movimientos ya revertidos

    # ---- helpers internos ----

    def _aplicar(self, movimiento, deltas):
        """Valida y aplica un movimiento. Idempotente; no deja efectos si falla."""
        identificador = movimiento["id"]
        existente = self._indice.get(identificador)
        if existente is not None:
            if existente == movimiento:
                return
            raise ValueError("identificador reusado con argumentos distintos")

        # Validación completa antes de tocar el estado.
        for ubicacion, delta in deltas.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError("saldo insuficiente")

        for ubicacion, delta in deltas.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta
        self._indice[identificador] = movimiento
        self._historial.append(movimiento)

    @staticmethod
    def _movimiento(identificador, tipo, origen, destino, cantidad, original=None):
        return {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    # ---- API pública ----

    def saldo(self, ubicacion):
        _texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        _texto(id, "el identificador")
        _texto(ubicacion, "la ubicación")
        _cantidad(cantidad)
        mov = self._movimiento(id, "ingreso", None, ubicacion, cantidad)
        self._aplicar(mov, _efecto(mov))

    def retirar(self, id, ubicacion, cantidad):
        _texto(id, "el identificador")
        _texto(ubicacion, "la ubicación")
        _cantidad(cantidad)
        mov = self._movimiento(id, "retiro", ubicacion, None, cantidad)
        self._aplicar(mov, _efecto(mov))

    def transferir(self, id, origen, destino, cantidad):
        _texto(id, "el identificador")
        _texto(origen, "el origen")
        _texto(destino, "el destino")
        _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        mov = self._movimiento(id, "transferencia", origen, destino, cantidad)
        self._aplicar(mov, _efecto(mov))

    def revertir(self, id, original):
        _texto(id, "el identificador")
        _texto(original, "el identificador original")

        existente = self._indice.get(id)
        if existente is not None:
            if existente["tipo"] == "reversion" and existente["original"] == original:
                return  # repetición idéntica: no hace nada
            raise ValueError("identificador reusado con argumentos distintos")

        mov_original = self._indice.get(original)
        if mov_original is None:
            raise ValueError("movimiento original inexistente")
        if mov_original["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        # Deltas inversos a los del original.
        deltas = {u: -d for u, d in _efecto(mov_original).items()}
        mov = self._movimiento(
            id,
            "reversion",
            mov_original["destino"],
            mov_original["origen"],
            mov_original["cantidad"],
            original,
        )
        self._aplicar(mov, deltas)
        self._revertidos.add(original)

    def historial(self):
        return [dict(m) for m in self._historial]
