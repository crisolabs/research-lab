"""Libro de inventario."""


def _texto(valor):
    if not isinstance(valor, str) or not valor:
        raise ValueError("se requiere un string no vacío")
    return valor


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("cantidad inválida")
    return valor


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._por_id = {}  # id -> (firma, movimiento)
        self._revertidos = set()

    def saldo(self, ubicacion):
        _texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _ya_aplicado(self, id_, firma):
        previo = self._por_id.get(id_)
        if previo is None:
            return False
        if previo[0] != firma:
            raise ValueError("identificador reutilizado con argumentos distintos")
        return True

    def _aplicar(self, id_, firma, mov, cambios):
        nuevos = {}
        for ub, delta in cambios:
            actual = nuevos.get(ub, self._saldos.get(ub, 0))
            nuevos[ub] = actual + delta
        if any(v < 0 for v in nuevos.values()):
            raise ValueError("saldo insuficiente")
        self._saldos.update(nuevos)
        self._historial.append(mov)
        self._por_id[id_] = (firma, mov)

    def ingresar(self, id, ubicacion, cantidad):
        _texto(id); _texto(ubicacion); _cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        mov = {"id": id, "tipo": "ingreso", "origen": None,
               "destino": ubicacion, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, mov, [(ubicacion, cantidad)])
        return None

    def retirar(self, id, ubicacion, cantidad):
        _texto(id); _texto(ubicacion); _cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        mov = {"id": id, "tipo": "retiro", "origen": ubicacion,
               "destino": None, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, mov, [(ubicacion, -cantidad)])
        return None

    def transferir(self, id, origen, destino, cantidad):
        _texto(id); _texto(origen); _texto(destino); _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        mov = {"id": id, "tipo": "transferencia", "origen": origen,
               "destino": destino, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, mov, [(origen, -cantidad), (destino, cantidad)])
        return None

    def revertir(self, id, original):
        _texto(id); _texto(original)
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        previo = self._por_id.get(original)
        if previo is None:
            raise ValueError("movimiento original inexistente")
        orig = previo[1]
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("movimiento ya revertido")
        cambios = []
        if orig["destino"] is not None:
            cambios.append((orig["destino"], -orig["cantidad"]))
        if orig["origen"] is not None:
            cambios.append((orig["origen"], orig["cantidad"]))
        mov = {"id": id, "tipo": "reversion", "origen": orig["destino"],
               "destino": orig["origen"], "cantidad": orig["cantidad"],
               "original": original}
        self._aplicar(id, firma, mov, cambios)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [dict(m) for m in self._historial]
