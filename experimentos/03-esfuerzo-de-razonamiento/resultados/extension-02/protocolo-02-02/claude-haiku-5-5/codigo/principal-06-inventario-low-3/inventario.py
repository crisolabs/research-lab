"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> (firma de la operación, entrada del historial)
        self._ids = {}
        # originales ya revertidos
        self._revertidos = set()

    # ----- consultas -----

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "ubicación")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(entrada) for entrada in self._historial]

    # ----- internos -----

    def _aplicar(self, cambios):
        """Aplica un diccionario {ubicacion: delta} de forma atómica."""
        nuevos = {}
        for ubicacion, delta in cambios.items():
            nuevo = self._saldos.get(ubicacion, 0) + delta
            if nuevo < 0:
                raise ValueError("saldo insuficiente")
            nuevos[ubicacion] = nuevo
        self._saldos.update(nuevos)

    def _registrar(self, id_, firma, entrada):
        self._ids[id_] = (firma, entrada)
        self._historial.append(entrada)

    def _chequear_id(self, id_, firma):
        """Devuelve True si la operación ya fue aplicada; ValueError si el id está en uso con otros argumentos."""
        if id_ in self._ids:
            if self._ids[id_][0] == firma:
                return True
            raise ValueError("identificador reusado con argumentos distintos")
        return False

    @staticmethod
    def _deltas(origen, destino, cantidad):
        cambios = {}
        if origen is not None:
            cambios[origen] = cambios.get(origen, 0) - cantidad
        if destino is not None:
            cambios[destino] = cambios.get(destino, 0) + cantidad
        return cambios

    # ----- mutaciones -----

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "identificador")
        _validar_texto(ubicacion, "ubicación")
        _validar_cantidad(cantidad)
        firma = ("ingreso", None, ubicacion, cantidad, None)
        if self._chequear_id(id, firma):
            return None
        self._aplicar(self._deltas(None, ubicacion, cantidad))
        self._registrar(id, firma, {
            "id": id, "tipo": "ingreso", "origen": None,
            "destino": ubicacion, "cantidad": cantidad, "original": None,
        })
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "identificador")
        _validar_texto(ubicacion, "ubicación")
        _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, None, cantidad, None)
        if self._chequear_id(id, firma):
            return None
        self._aplicar(self._deltas(ubicacion, None, cantidad))
        self._registrar(id, firma, {
            "id": id, "tipo": "retiro", "origen": ubicacion,
            "destino": None, "cantidad": cantidad, "original": None,
        })
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "identificador")
        _validar_texto(origen, "ubicación de origen")
        _validar_texto(destino, "ubicación de destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad, None)
        if self._chequear_id(id, firma):
            return None
        self._aplicar(self._deltas(origen, destino, cantidad))
        self._registrar(id, firma, {
            "id": id, "tipo": "transferencia", "origen": origen,
            "destino": destino, "cantidad": cantidad, "original": None,
        })
        return None

    def revertir(self, id, original):
        _validar_texto(id, "identificador")
        _validar_texto(original, "identificador original")
        firma = ("revertir", original)
        if self._chequear_id(id, firma):
            return None
        if original not in self._ids:
            raise ValueError("movimiento original inexistente")
        entrada_orig = self._ids[original][1]
        if entrada_orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("movimiento ya revertido")
        # Invertir origen/destino respecto del original.
        origen = entrada_orig["destino"]
        destino = entrada_orig["origen"]
        cantidad = entrada_orig["cantidad"]
        self._aplicar(self._deltas(origen, destino, cantidad))
        self._revertidos.add(original)
        self._registrar(id, firma, {
            "id": id, "tipo": "reversion", "origen": origen,
            "destino": destino, "cantidad": cantidad, "original": original,
        })
        return None
