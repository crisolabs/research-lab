"""Libro de inventario."""

import copy


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
        self._ops = {}  # id -> (firma, entrada)
        self._revertidos = set()

    def saldo(self, ubicacion):
        _texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def _ya_aplicado(self, id, firma):
        _texto(id)
        if id in self._ops:
            if self._ops[id][0] == firma:
                return True
            raise ValueError("identificador reutilizado con otros argumentos")
        return False

    def _aplicar(self, id, firma, entrada, deltas):
        nuevos = {}
        for ubic, d in deltas:
            nuevos[ubic] = nuevos.get(ubic, self._saldos.get(ubic, 0)) + d
        if any(v < 0 for v in nuevos.values()):
            raise ValueError("saldo insuficiente")
        self._saldos.update(nuevos)
        self._historial.append(entrada)
        self._ops[id] = (firma, entrada)

    def _movimiento(self, id, tipo, origen, destino, cantidad):
        _texto(id)
        if origen is not None:
            _texto(origen)
        if destino is not None:
            _texto(destino)
        _cantidad(cantidad)
        if tipo == "transferencia" and origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = (tipo, origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        deltas = []
        if origen is not None:
            deltas.append((origen, -cantidad))
        if destino is not None:
            deltas.append((destino, cantidad))
        entrada = {"id": id, "tipo": tipo, "origen": origen,
                   "destino": destino, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, entrada, deltas)
        return None

    def ingresar(self, id, ubicacion, cantidad):
        _texto(ubicacion)
        return self._movimiento(id, "ingreso", None, ubicacion, cantidad)

    def retirar(self, id, ubicacion, cantidad):
        _texto(ubicacion)
        return self._movimiento(id, "retiro", ubicacion, None, cantidad)

    def transferir(self, id, origen, destino, cantidad):
        _texto(origen)
        _texto(destino)
        return self._movimiento(id, "transferencia", origen, destino, cantidad)

    def revertir(self, id, original):
        _texto(id)
        _texto(original)
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        if original not in self._ops:
            raise ValueError("movimiento original inexistente")
        orig = self._ops[original][1]
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("movimiento ya revertido")
        origen, destino, cant = orig["destino"], orig["origen"], orig["cantidad"]
        deltas = []
        if origen is not None:
            deltas.append((origen, -cant))
        if destino is not None:
            deltas.append((destino, cant))
        entrada = {"id": id, "tipo": "reversion", "origen": origen,
                   "destino": destino, "cantidad": cant, "original": original}
        self._aplicar(id, firma, entrada, deltas)
        self._revertidos.add(original)
        return None

    def historial(self):
        return copy.deepcopy(self._historial)
