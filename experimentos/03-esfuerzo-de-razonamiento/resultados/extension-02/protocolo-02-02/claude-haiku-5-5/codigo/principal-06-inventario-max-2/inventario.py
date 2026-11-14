"""Implementá el libro de inventario pedido en TAREA.md."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._por_id = {}
        self._revertidos = set()

    def saldo(self, ubicacion):
        ubicacion = _texto(ubicacion, "La ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "El identificador")
        ubicacion = _texto(ubicacion, "La ubicación")
        cantidad = _cantidad(cantidad)
        registro = _registro(id, "ingreso", None, ubicacion, cantidad, None)
        if not self._ya_aplicado(registro):
            self._aplicar(registro)

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "El identificador")
        ubicacion = _texto(ubicacion, "La ubicación")
        cantidad = _cantidad(cantidad)
        registro = _registro(id, "retiro", ubicacion, None, cantidad, None)
        if self._ya_aplicado(registro):
            return
        self._exigir_fondos(ubicacion, cantidad)
        self._aplicar(registro)

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "El identificador")
        origen = _texto(origen, "La ubicación de origen")
        destino = _texto(destino, "La ubicación de destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("El origen y el destino deben ser distintos")
        registro = _registro(id, "transferencia", origen, destino, cantidad, None)
        if self._ya_aplicado(registro):
            return
        self._exigir_fondos(origen, cantidad)
        self._aplicar(registro)

    def revertir(self, id, original):
        id = _texto(id, "El identificador")
        original = _texto(original, "El identificador original")
        movimiento = self._por_id.get(original)
        if movimiento is None:
            raise ValueError(f"El movimiento original {original!r} no existe")
        registro = _registro(
            id,
            "reversion",
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )
        if self._ya_aplicado(registro):
            return
        if movimiento["tipo"] == "reversion":
            raise ValueError("No se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"El movimiento {original!r} ya fue revertido")
        if registro["origen"] is not None:
            self._exigir_fondos(registro["origen"], registro["cantidad"])
        self._aplicar(registro)
        self._revertidos.add(original)

    def historial(self):
        return [dict(registro) for registro in self._historial]

    def _ya_aplicado(self, registro):
        previo = self._por_id.get(registro["id"])
        if previo is None:
            return False
        if previo != registro:
            raise ValueError(f"El identificador {registro['id']!r} ya se usó con otros datos")
        return True

    def _exigir_fondos(self, ubicacion, cantidad):
        if self._saldos.get(ubicacion, 0) < cantidad:
            raise ValueError(f"Saldo insuficiente en {ubicacion!r}")

    def _aplicar(self, registro):
        cantidad = registro["cantidad"]
        if registro["origen"] is not None:
            origen = registro["origen"]
            self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
        if registro["destino"] is not None:
            destino = registro["destino"]
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._por_id[registro["id"]] = registro
        self._historial.append(registro)


def _texto(valor, nombre):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("La cantidad debe ser un entero positivo")
    return int(valor)


def _registro(id_, tipo, origen, destino, cantidad, original):
    return {
        "id": id_,
        "tipo": tipo,
        "origen": origen,
        "destino": destino,
        "cantidad": cantidad,
        "original": original,
    }
