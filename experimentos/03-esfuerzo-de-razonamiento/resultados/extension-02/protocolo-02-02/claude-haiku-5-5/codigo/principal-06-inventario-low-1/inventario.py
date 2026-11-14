"""Implementá el libro de inventario pedido en TAREA.md."""


def _validar_texto(valor):
    if not isinstance(valor, str) or not valor:
        raise ValueError("se esperaba un string no vacío")
    return valor


def _validar_cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


class Inventario:
    def __init__(self):
        self._saldos = {}
        # id -> (firma de la solicitud, registro del movimiento)
        self._movs = {}
        # Lista de registros en orden de aplicación.
        self._hist = []
        # Identificadores de movimientos ya revertidos.
        self._revertidos = set()

    # ----- auxiliares -----

    def _repetido(self, mid, firma):
        """True si el id ya existe con la misma operación y argumentos.

        Lanza ValueError si el id existe con argumentos distintos.
        """
        if mid not in self._movs:
            return False
        if self._movs[mid][0] == firma:
            return True
        raise ValueError(f"identificador reusado con argumentos distintos: {mid!r}")

    def _asentar(self, mid, firma, registro):
        self._movs[mid] = (firma, registro)
        self._hist.append(registro)

    # ----- consultas -----

    def saldo(self, ubicacion):
        _validar_texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(r) for r in self._hist]

    # ----- mutaciones -----

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id)
        _validar_texto(ubicacion)
        _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None
        self._saldos[ubicacion] = self.saldo(ubicacion) + cantidad
        self._asentar(id, firma, {
            "id": id, "tipo": "ingreso", "origen": None,
            "destino": ubicacion, "cantidad": cantidad, "original": None,
        })
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id)
        _validar_texto(ubicacion)
        _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._repetido(id, firma):
            return None
        if self.saldo(ubicacion) < cantidad:
            raise ValueError("saldo insuficiente")
        self._saldos[ubicacion] -= cantidad
        self._asentar(id, firma, {
            "id": id, "tipo": "retiro", "origen": ubicacion,
            "destino": None, "cantidad": cantidad, "original": None,
        })
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id)
        _validar_texto(origen)
        _validar_texto(destino)
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._repetido(id, firma):
            return None
        if self.saldo(origen) < cantidad:
            raise ValueError("saldo insuficiente")
        self._saldos[origen] -= cantidad
        self._saldos[destino] = self.saldo(destino) + cantidad
        self._asentar(id, firma, {
            "id": id, "tipo": "transferencia", "origen": origen,
            "destino": destino, "cantidad": cantidad, "original": None,
        })
        return None

    def revertir(self, id, original):
        _validar_texto(id)
        _validar_texto(original)
        firma = ("reversion", original)
        if self._repetido(id, firma):
            return None
        if original not in self._movs:
            raise ValueError("movimiento original inexistente")
        orig = self._movs[original][1]
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        cantidad = orig["cantidad"]
        # Efectos invertidos: origen y destino intercambiados.
        rev_origen = orig["destino"]
        rev_destino = orig["origen"]
        if rev_origen is not None and self.saldo(rev_origen) < cantidad:
            raise ValueError("la reversión dejaría un saldo negativo")

        if rev_origen is not None:
            self._saldos[rev_origen] = self.saldo(rev_origen) - cantidad
        if rev_destino is not None:
            self._saldos[rev_destino] = self.saldo(rev_destino) + cantidad
        self._revertidos.add(original)
        self._asentar(id, firma, {
            "id": id, "tipo": "reversion", "origen": rev_origen,
            "destino": rev_destino, "cantidad": cantidad, "original": original,
        })
        return None
