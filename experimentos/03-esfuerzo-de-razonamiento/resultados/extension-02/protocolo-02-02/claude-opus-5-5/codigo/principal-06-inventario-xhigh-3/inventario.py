"""Libro de inventario con movimientos idempotentes y reversiones."""

import threading


class Inventario:
    """Libro de inventario por ubicación con historial de movimientos."""

    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> registro del movimiento (diccionario guardado en el historial)
        self._movimientos = {}
        # id de movimiento original -> id de la reversión que lo revirtió
        self._revertidos = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or len(valor) == 0:
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @classmethod
    def _validar_ubicacion(cls, ubicacion, nombre="ubicacion"):
        cls._validar_texto(ubicacion, nombre)

    @classmethod
    def _validar_id(cls, id_, nombre="id"):
        cls._validar_texto(id_, nombre)

    @staticmethod
    def _validar_cantidad(cantidad):
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            raise ValueError("cantidad debe ser un entero positivo")

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _saldo(self, ubicacion):
        return self._saldos.get(ubicacion, 0)

    @staticmethod
    def _variaciones(origen, destino, cantidad):
        """Variaciones de saldo de mover `cantidad` de origen a destino."""
        variaciones = {}
        if origen is not None:
            variaciones[origen] = variaciones.get(origen, 0) - cantidad
        if destino is not None:
            variaciones[destino] = variaciones.get(destino, 0) + cantidad
        return variaciones

    def _calcular_nuevos_saldos(self, variaciones):
        nuevos = {}
        for ubicacion, delta in variaciones.items():
            nuevo = self._saldo(ubicacion) + delta
            if nuevo < 0:
                raise ValueError(
                    f"saldo insuficiente en la ubicación {ubicacion!r}"
                )
            nuevos[ubicacion] = nuevo
        return nuevos

    def _ya_registrado(self, id_, tipo, origen, destino, cantidad, original):
        """Indica si `id_` ya existe con los mismos datos.

        Devuelve True si es una repetición idéntica (no se hace nada),
        False si el identificador es nuevo, y lanza ValueError si el
        identificador ya se usó con otros datos.
        """
        registro = self._movimientos.get(id_)
        if registro is None:
            return False
        if (
            registro["tipo"] == tipo
            and registro["origen"] == origen
            and registro["destino"] == destino
            and registro["cantidad"] == cantidad
            and registro["original"] == original
        ):
            return True
        raise ValueError(f"el identificador {id_!r} ya se usó con otros datos")

    def _aplicar(self, id_, tipo, origen, destino, cantidad, original):
        variaciones = self._variaciones(origen, destino, cantidad)
        nuevos = self._calcular_nuevos_saldos(variaciones)
        registro = {
            "id": id_,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        # A partir de aquí no se lanzan excepciones: se confirma todo junto.
        self._saldos.update(nuevos)
        self._movimientos[id_] = registro
        self._historial.append(registro)
        if original is not None:
            self._revertidos[original] = id_

    def _registrar(self, id_, tipo, origen, destino, cantidad):
        with self._lock:
            if self._ya_registrado(id_, tipo, origen, destino, cantidad, None):
                return
            self._aplicar(id_, tipo, origen, destino, cantidad, None)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def saldo(self, ubicacion):
        self._validar_ubicacion(ubicacion)
        with self._lock:
            return self._saldo(ubicacion)

    def ingresar(self, id, ubicacion, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(ubicacion)
        self._validar_cantidad(cantidad)
        self._registrar(id, "ingreso", None, ubicacion, int(cantidad))
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(ubicacion)
        self._validar_cantidad(cantidad)
        self._registrar(id, "retiro", ubicacion, None, int(cantidad))
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_id(id)
        self._validar_ubicacion(origen, "origen")
        self._validar_ubicacion(destino, "destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._registrar(id, "transferencia", origen, destino, int(cantidad))
        return None

    def revertir(self, id, original):
        self._validar_id(id)
        self._validar_id(original, "original")
        with self._lock:
            existente = self._movimientos.get(id)
            if existente is not None:
                if (
                    existente["tipo"] == "reversion"
                    and existente["original"] == original
                ):
                    return None
                raise ValueError(
                    f"el identificador {id!r} ya se usó con otros datos"
                )
            movimiento = self._movimientos.get(original)
            if movimiento is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if movimiento["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")
            self._aplicar(
                id,
                "reversion",
                movimiento["destino"],
                movimiento["origen"],
                movimiento["cantidad"],
                original,
            )
        return None

    def historial(self):
        with self._lock:
            return [dict(registro) for registro in self._historial]
