"""Libro de inventario."""


def _ubic(u):
    if not isinstance(u, str) or not u:
        raise ValueError("ubicación inválida")
    return u


def _ident(i):
    if not isinstance(i, str) or not i:
        raise ValueError("identificador inválido")
    return i


def _cant(c):
    if isinstance(c, bool) or not isinstance(c, int) or c <= 0:
        raise ValueError("cantidad inválida")
    return c


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._ops = {}  # id -> (firma, indice historial)
        self._revertidos = set()

    def saldo(self, ubicacion):
        return self._saldos.get(_ubic(ubicacion), 0)

    def _ya_aplicado(self, id, firma):
        if id in self._ops:
            if self._ops[id][0] == firma:
                return True
            raise ValueError("identificador reutilizado con otros argumentos")
        return False

    def _aplicar(self, id, firma, tipo, origen, destino, cantidad, original=None):
        nuevos = dict(self._saldos)
        if origen is not None:
            r = nuevos.get(origen, 0) - cantidad
            if r < 0:
                raise ValueError("saldo insuficiente")
            nuevos[origen] = r
        if destino is not None:
            nuevos[destino] = nuevos.get(destino, 0) + cantidad
        self._saldos = nuevos
        self._ops[id] = (firma, len(self._historial))
        self._historial.append({
            "id": id, "tipo": tipo, "origen": origen, "destino": destino,
            "cantidad": cantidad, "original": original,
        })

    def ingresar(self, id, ubicacion, cantidad):
        _ident(id); _ubic(ubicacion); _cant(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(id, firma, "ingreso", None, ubicacion, cantidad)
        return None

    def retirar(self, id, ubicacion, cantidad):
        _ident(id); _ubic(ubicacion); _cant(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(id, firma, "retiro", ubicacion, None, cantidad)
        return None

    def transferir(self, id, origen, destino, cantidad):
        _ident(id); _ubic(origen); _ubic(destino); _cant(cantidad)
        if origen == destino:
            raise ValueError("origen y destino iguales")
        firma = ("transferencia", origen, destino, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        self._aplicar(id, firma, "transferencia", origen, destino, cantidad)
        return None

    def revertir(self, id, original):
        _ident(id); _ident(original)
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        if original not in self._ops:
            raise ValueError("movimiento original inexistente")
        mov = self._historial[self._ops[original][1]]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("movimiento ya revertido")
        self._aplicar(id, firma, "reversion", mov["destino"], mov["origen"],
                      mov["cantidad"], original)
        self._revertidos.add(original)
        return None

    def historial(self):
        return [dict(m) for m in self._historial]
