"""Implementá el libro de inventario pedido en TAREA.md."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _validar_cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return int(valor)


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._movimientos = {}
        self._firmas = {}
        self._revertidos = set()

    def saldo(self, ubicacion):
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "el identificador")
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
        self._asentar(firma, {
            "id": id,
            "tipo": "ingreso",
            "origen": None,
            "destino": ubicacion,
            "cantidad": cantidad,
            "original": None,
        })
        return None

    def retirar(self, id, ubicacion, cantidad):
        id = _validar_texto(id, "el identificador")
        ubicacion = _validar_texto(ubicacion, "la ubicación")
        cantidad = _validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        disponible = self._saldos.get(ubicacion, 0)
        if disponible < cantidad:
            raise ValueError(f"saldo insuficiente en {ubicacion!r}")
        self._saldos[ubicacion] = disponible - cantidad
        self._asentar(firma, {
            "id": id,
            "tipo": "retiro",
            "origen": ubicacion,
            "destino": None,
            "cantidad": cantidad,
            "original": None,
        })
        return None

    def transferir(self, id, origen, destino, cantidad):
        id = _validar_texto(id, "el identificador")
        origen = _validar_texto(origen, "la ubicación de origen")
        destino = _validar_texto(destino, "la ubicación de destino")
        cantidad = _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        disponible = self._saldos.get(origen, 0)
        if disponible < cantidad:
            raise ValueError(f"saldo insuficiente en {origen!r}")
        self._saldos[origen] = disponible - cantidad
        self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._asentar(firma, {
            "id": id,
            "tipo": "transferencia",
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": None,
        })
        return None

    def revertir(self, id, original):
        id = _validar_texto(id, "el identificador")
        original = _validar_texto(original, "el identificador original")
        firma = ("revertir", original)
        if self._ya_aplicado(id, firma):
            return None
        if original not in self._movimientos:
            raise ValueError(f"no existe el movimiento {original!r}")
        mov = self._movimientos[original]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        origen = mov["origen"]
        destino = mov["destino"]
        cantidad = mov["cantidad"]
        cambios = {}
        if origen is not None:
            cambios[origen] = cambios.get(origen, 0) + cantidad
        if destino is not None:
            cambios[destino] = cambios.get(destino, 0) - cantidad
        for ubicacion, delta in cambios.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError(
                    f"la reversión dejaría negativo el saldo de {ubicacion!r}"
                )
        for ubicacion, delta in cambios.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta
        self._revertidos.add(original)
        self._asentar(firma, {
            "id": id,
            "tipo": "reversion",
            "origen": destino,
            "destino": origen,
            "cantidad": cantidad,
            "original": original,
        })
        return None

    def historial(self):
        return [dict(movimiento) for movimiento in self._historial]

    def _ya_aplicado(self, id, firma):
        if id not in self._firmas:
            return False
        if self._firmas[id] != firma:
            raise ValueError(
                f"el identificador {id!r} ya se usó con otros argumentos"
            )
        return True

    def _asentar(self, firma, movimiento):
        self._historial.append(movimiento)
        self._movimientos[movimiento["id"]] = movimiento
        self._firmas[movimiento["id"]] = firma
