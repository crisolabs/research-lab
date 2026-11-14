"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._firmas = {}  # id -> firma (operación, argumentos)
        self._movimientos = {}  # id -> registro del historial
        self._revertidos = set()  # ids de movimientos ya revertidos

    # -- utilidades internas -------------------------------------------
    def _chequear_id(self, id_, firma):
        """Devuelve True si es una repetición idempotente; ValueError si choca."""
        previa = self._firmas.get(id_)
        if previa is None:
            return False
        if previa == firma:
            return True
        raise ValueError(f"identificador {id_!r} ya usado con otros argumentos")

    def _aplicar(self, id_, firma, variaciones, registro):
        nuevos = {}
        for ubic, delta in variaciones:
            nuevos[ubic] = nuevos.get(ubic, self._saldos.get(ubic, 0)) + delta
        for ubic, valor in nuevos.items():
            if valor < 0:
                raise ValueError(f"saldo insuficiente en {ubic!r}")
        self._saldos.update(nuevos)
        self._firmas[id_] = firma
        self._movimientos[id_] = registro
        self._historial.append(registro)

    # -- consultas -----------------------------------------------------
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "ubicacion")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(r) for r in self._historial]

    # -- mutaciones ----------------------------------------------------
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._chequear_id(id, firma):
            return None
        registro = {"id": id, "tipo": "ingreso", "origen": None,
                    "destino": ubicacion, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, [(ubicacion, cantidad)], registro)
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._chequear_id(id, firma):
            return None
        registro = {"id": id, "tipo": "retiro", "origen": ubicacion,
                    "destino": None, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, [(ubicacion, -cantidad)], registro)
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "id")
        _validar_texto(origen, "origen")
        _validar_texto(destino, "destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferencia", origen, destino, cantidad)
        if self._chequear_id(id, firma):
            return None
        registro = {"id": id, "tipo": "transferencia", "origen": origen,
                    "destino": destino, "cantidad": cantidad, "original": None}
        self._aplicar(id, firma, [(origen, -cantidad), (destino, cantidad)], registro)
        return None

    def revertir(self, id, original):
        _validar_texto(id, "id")
        _validar_texto(original, "original")
        firma = ("reversion", original)
        if self._chequear_id(id, firma):
            return None
        mov = self._movimientos.get(original)
        if mov is None:
            raise ValueError(f"movimiento {original!r} inexistente")
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"movimiento {original!r} ya revertido")
        cantidad = mov["cantidad"]
        variaciones = []
        if mov["destino"] is not None:
            variaciones.append((mov["destino"], -cantidad))
        if mov["origen"] is not None:
            variaciones.append((mov["origen"], cantidad))
        registro = {"id": id, "tipo": "reversion", "origen": mov["destino"],
                    "destino": mov["origen"], "cantidad": cantidad,
                    "original": original}
        self._aplicar(id, firma, variaciones, registro)
        self._revertidos.add(original)
        return None
