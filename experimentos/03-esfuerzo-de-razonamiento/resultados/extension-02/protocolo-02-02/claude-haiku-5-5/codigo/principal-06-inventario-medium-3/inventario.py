"""Implementá el libro de inventario pedido en TAREA.md."""

from copy import deepcopy


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return cantidad


class Inventario:
    """Libro de inventario con saldos por ubicación e historial de movimientos."""

    def __init__(self):
        self._saldos = {}
        self._movimientos = {}   # id -> registro (dict)
        self._orden = []         # ids en orden de aplicación
        self._revertidos = {}    # id original -> id de la reversión

    # ---- consultas ----

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [deepcopy(self._movimientos[i]) for i in self._orden]

    # ---- mutaciones ----

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "ingreso", None, ubicacion, cantidad, None)
        if self._es_repeticion(id, registro):
            return None
        self._aplicar(registro, [(ubicacion, cantidad)], [])
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        registro = self._registro(id, "retiro", ubicacion, None, cantidad, None)
        if self._es_repeticion(id, registro):
            return None
        self._aplicar(registro, [], [(ubicacion, cantidad)])
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        registro = self._registro(id, "transferencia", origen, destino, cantidad, None)
        if self._es_repeticion(id, registro):
            return None
        self._aplicar(registro, [(destino, cantidad)], [(origen, cantidad)])
        return None

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el original")
        if original not in self._movimientos:
            raise ValueError("el movimiento original no existe")
        mov = self._movimientos[original]
        registro = self._registro(
            id, "reversion", mov["destino"], mov["origen"], mov["cantidad"], original
        )
        if self._es_repeticion(id, registro):
            return None
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")

        # Efectos de la reversión: quitar lo que el original sumó y devolver lo que restó.
        sumas = []
        restas = []
        if mov["origen"] is not None:
            sumas.append((mov["origen"], mov["cantidad"]))
        if mov["destino"] is not None:
            restas.append((mov["destino"], mov["cantidad"]))
        # Validar que ningún saldo quede negativo antes de aplicar.
        self._verificar_saldos(sumas, restas)
        self._aplicar(registro, sumas, restas)
        self._revertidos[original] = id
        return None

    # ---- auxiliares internos ----

    def _registro(self, id, tipo, origen, destino, cantidad, original):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _es_repeticion(self, id, registro):
        """True si el id ya existe con la misma operación; ValueError si difiere."""
        if id not in self._movimientos:
            return False
        if self._movimientos[id] == registro:
            return True
        raise ValueError("identificador reusado con argumentos distintos")

    def _verificar_saldos(self, sumas, restas):
        delta = {}
        for ubic, cant in sumas:
            delta[ubic] = delta.get(ubic, 0) + cant
        for ubic, cant in restas:
            delta[ubic] = delta.get(ubic, 0) - cant
        for ubic, d in delta.items():
            if self._saldos.get(ubic, 0) + d < 0:
                raise ValueError("saldo insuficiente")

    def _aplicar(self, registro, sumas, restas):
        self._verificar_saldos(sumas, restas)
        for ubic, cant in sumas:
            self._saldos[ubic] = self._saldos.get(ubic, 0) + cant
        for ubic, cant in restas:
            self._saldos[ubic] = self._saldos.get(ubic, 0) - cant
        self._movimientos[registro["id"]] = registro
        self._orden.append(registro["id"])
