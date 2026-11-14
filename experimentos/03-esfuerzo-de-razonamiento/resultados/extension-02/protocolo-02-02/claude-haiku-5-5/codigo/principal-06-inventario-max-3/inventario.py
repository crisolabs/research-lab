def _texto(valor, nombre):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return int(valor)


def _movimiento(identificador, tipo, origen, destino, cantidad, original):
    return {
        "id": identificador,
        "tipo": tipo,
        "origen": origen,
        "destino": destino,
        "cantidad": cantidad,
        "original": original,
    }


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._movimientos = {}
        self._revertidos = set()

    def saldo(self, ubicacion):
        return self._saldos.get(_texto(ubicacion, "la ubicación"), 0)

    def ingresar(self, id, ubicacion, cantidad):
        _texto(id, "el identificador")
        _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        mov = _movimiento(id, "ingreso", None, ubicacion, cantidad, None)
        if not self._ya_aplicado(mov):
            self._aplicar(mov)

    def retirar(self, id, ubicacion, cantidad):
        _texto(id, "el identificador")
        _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        mov = _movimiento(id, "retiro", ubicacion, None, cantidad, None)
        if not self._ya_aplicado(mov):
            self._aplicar(mov)

    def transferir(self, id, origen, destino, cantidad):
        _texto(id, "el identificador")
        _texto(origen, "el origen")
        _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        mov = _movimiento(id, "transferencia", origen, destino, cantidad, None)
        if not self._ya_aplicado(mov):
            self._aplicar(mov)

    def revertir(self, id, original):
        _texto(id, "el identificador")
        _texto(original, "el identificador original")
        orig = self._movimientos.get(original)
        if orig is None:
            raise ValueError("el movimiento original no existe")
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        mov = _movimiento(
            id, "reversion", orig["destino"], orig["origen"], orig["cantidad"], original
        )
        if self._ya_aplicado(mov):
            return
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")
        self._aplicar(mov)
        self._revertidos.add(original)

    def historial(self):
        return [dict(mov) for mov in self._historial]

    def _ya_aplicado(self, mov):
        previo = self._movimientos.get(mov["id"])
        if previo is None:
            return False
        if previo != mov:
            raise ValueError("identificador reusado con otra operación o argumentos")
        return True

    def _aplicar(self, mov):
        origen, destino, cantidad = mov["origen"], mov["destino"], mov["cantidad"]
        variaciones = {}
        if origen is not None:
            variaciones[origen] = -cantidad
        if destino is not None:
            variaciones[destino] = variaciones.get(destino, 0) + cantidad
        nuevos = {}
        for ubicacion, variacion in variaciones.items():
            nuevo = self._saldos.get(ubicacion, 0) + variacion
            if nuevo < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")
            nuevos[ubicacion] = nuevo
        self._saldos.update(nuevos)
        self._movimientos[mov["id"]] = mov
        self._historial.append(mov)
