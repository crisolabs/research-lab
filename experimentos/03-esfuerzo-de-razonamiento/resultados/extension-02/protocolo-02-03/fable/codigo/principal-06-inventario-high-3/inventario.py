"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading

_INGRESO = "ingreso"
_RETIRO = "retiro"
_TRANSFERENCIA = "transferencia"
_REVERSION = "reversion"


def _texto(valor, nombre):
    if not isinstance(valor, str) or len(valor) == 0:
        raise ValueError(f"{nombre} debe ser un string no vacío")
    # Normaliza subclases de str a un str exacto.
    return str.__str__(valor)


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError("la cantidad debe ser un entero positivo")
    valor = int.__int__(valor)
    if valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro
        self._orden = []  # ids en orden de aplicación
        self._revertidos = set()  # ids de movimientos ya revertidos
        self._candado = threading.RLock()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def saldo(self, ubicacion):
        ubicacion = _texto(ubicacion, "la ubicación")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._candado:
            return [dict(self._movimientos[i]) for i in self._orden]

    # ------------------------------------------------------------------
    # Mutaciones
    # ------------------------------------------------------------------
    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        registro = self._registro(id, _INGRESO, None, ubicacion, cantidad, None)
        with self._candado:
            if self._repetido(registro):
                return None
            self._aplicar(registro)
        return None

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        registro = self._registro(id, _RETIRO, ubicacion, None, cantidad, None)
        with self._candado:
            if self._repetido(registro):
                return None
            self._aplicar(registro)
        return None

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        registro = self._registro(
            id, _TRANSFERENCIA, origen, destino, cantidad, None
        )
        with self._candado:
            if self._repetido(registro):
                return None
            self._aplicar(registro)
        return None

    def revertir(self, id, original):
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo["tipo"] == _REVERSION and previo["original"] == original:
                    return None
                raise ValueError(
                    f"el identificador {id!r} ya fue usado con otros argumentos"
                )
            base = self._movimientos.get(original)
            if base is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if base["tipo"] == _REVERSION:
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            registro = self._registro(
                id,
                _REVERSION,
                base["destino"],
                base["origen"],
                base["cantidad"],
                original,
            )
            self._aplicar(registro)
            self._revertidos.add(original)
        return None

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    def _repetido(self, registro):
        """True si el id ya se aplicó con la misma operación y argumentos."""
        previo = self._movimientos.get(registro["id"])
        if previo is None:
            return False
        if previo == registro:
            return True
        raise ValueError(
            f"el identificador {registro['id']!r} ya fue usado con otros argumentos"
        )

    def _aplicar(self, registro):
        """Valida saldos y recién entonces aplica y registra el movimiento."""
        origen = registro["origen"]
        destino = registro["destino"]
        cantidad = registro["cantidad"]
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: "
                    f"hay {disponible}, se necesitan {cantidad}"
                )
            self._saldos[origen] = disponible - cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
        self._movimientos[registro["id"]] = registro
        self._orden.append(registro["id"])
