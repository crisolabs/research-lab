"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise ValueError("la cantidad debe ser un entero")
    if cantidad <= 0:
        raise ValueError("la cantidad debe ser positiva")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}  # id -> registro (mismo objeto que en _historial)
        self._historial = []
        self._revertidos = {}  # id original -> id de la reversión
        self._candado = threading.RLock()

    # ------------------------------------------------------------------ consultas

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        with self._candado:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._candado:
            return [dict(registro) for registro in self._historial]

    # ---------------------------------------------------------------- mutaciones

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "ingreso", None, ubicacion, cantidad, None))

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._aplicar(self._registro(id, "retiro", ubicacion, None, cantidad, None))

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._aplicar(
            self._registro(id, "transferencia", origen, destino, cantidad, None)
        )

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        with self._candado:
            previo = self._movimientos.get(id)
            if previo is not None:
                if previo["tipo"] == "reversion" and previo["original"] == original:
                    return
                raise ValueError(f"el identificador {id!r} ya fue usado")
            movimiento = self._movimientos.get(original)
            if movimiento is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if movimiento["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            registro = self._registro(
                id,
                "reversion",
                movimiento["destino"],
                movimiento["origen"],
                movimiento["cantidad"],
                original,
            )
            self._aplicar(registro)
            self._revertidos[original] = id

    # ------------------------------------------------------------------ internos

    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": int(cantidad),
            "original": original,
        }

    def _aplicar(self, registro):
        """Aplica el registro o falla sin dejar ningún efecto."""
        with self._candado:
            previo = self._movimientos.get(registro["id"])
            if previo is not None:
                if previo == registro:
                    return
                raise ValueError(
                    f"el identificador {registro['id']!r} ya fue usado "
                    "con otra operación o argumentos"
                )
            origen = registro["origen"]
            destino = registro["destino"]
            cantidad = registro["cantidad"]
            if origen is not None and self._saldos.get(origen, 0) < cantidad:
                raise ValueError(f"saldo insuficiente en {origen!r}")
            # A partir de acá nada puede fallar.
            if origen is not None:
                self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
            if destino is not None:
                self._saldos[destino] = self._saldos.get(destino, 0) + cantidad
            self._movimientos[registro["id"]] = registro
            self._historial.append(registro)
