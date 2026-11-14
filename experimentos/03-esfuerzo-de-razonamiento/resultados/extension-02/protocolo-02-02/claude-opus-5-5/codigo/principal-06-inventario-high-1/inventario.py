"""Libro de inventario con movimientos idempotentes y reversibles."""

import threading


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        # id -> firma de la operación (para idempotencia)
        self._firmas = {}
        # id -> registro del movimiento en el historial
        self._movimientos = {}
        # ids de movimientos originales ya revertidos
        self._revertidos = set()
        self._lock = threading.RLock()

    # ------------------------------------------------------------ validación
    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or valor == "":
            raise ValueError(f"{nombre} debe ser un string no vacío")

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")

    def _ya_aplicado(self, id, firma):
        """True si el id ya existe con la misma firma; ValueError si difiere."""
        previa = self._firmas.get(id)
        if previa is None:
            return False
        if previa != firma:
            raise ValueError(f"el identificador {id!r} ya se usó con otros argumentos")
        return True

    def _registrar(self, id, firma, tipo, origen, destino, cantidad, original):
        registro = {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        self._firmas[id] = firma
        self._movimientos[id] = registro
        self._historial.append(registro)

    # ------------------------------------------------------------- consultas
    def saldo(self, ubicacion):
        self._validar_texto(ubicacion, "la ubicación")
        with self._lock:
            return self._saldos.get(ubicacion, 0)

    def historial(self):
        with self._lock:
            return [dict(r) for r in self._historial]

    # ------------------------------------------------------------ mutaciones
    def ingresar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + cantidad
            self._registrar(id, firma, "ingreso", None, ubicacion, cantidad, None)
        return None

    def retirar(self, id, ubicacion, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(ubicacion, "la ubicación")
        self._validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            actual = self._saldos.get(ubicacion, 0)
            if actual < cantidad:
                raise ValueError("saldo insuficiente")
            self._saldos[ubicacion] = actual - cantidad
            self._registrar(id, firma, "retiro", ubicacion, None, cantidad, None)
        return None

    def transferir(self, id, origen, destino, cantidad):
        self._validar_texto(id, "el identificador")
        self._validar_texto(origen, "el origen")
        self._validar_texto(destino, "el destino")
        self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            saldo_origen = self._saldos.get(origen, 0)
            if saldo_origen < cantidad:
                raise ValueError("saldo insuficiente")
            saldo_destino = self._saldos.get(destino, 0)
            self._saldos[origen] = saldo_origen - cantidad
            self._saldos[destino] = saldo_destino + cantidad
            self._registrar(id, firma, "transferencia", origen, destino, cantidad, None)
        return None

    def revertir(self, id, original):
        self._validar_texto(id, "el identificador")
        self._validar_texto(original, "el movimiento original")
        firma = ("revertir", original)
        with self._lock:
            if self._ya_aplicado(id, firma):
                return None
            mov = self._movimientos.get(original)
            if mov is None:
                raise ValueError(f"no existe el movimiento {original!r}")
            if mov["tipo"] == "reversion":
                raise ValueError("no se puede revertir una reversión")
            if original in self._revertidos:
                raise ValueError(f"el movimiento {original!r} ya fue revertido")

            cantidad = mov["cantidad"]
            # Variaciones inversas: el destino original pierde, el origen gana.
            variaciones = {}
            if mov["destino"] is not None:
                variaciones[mov["destino"]] = variaciones.get(mov["destino"], 0) - cantidad
            if mov["origen"] is not None:
                variaciones[mov["origen"]] = variaciones.get(mov["origen"], 0) + cantidad

            nuevos = {}
            for ubicacion, delta in variaciones.items():
                valor = self._saldos.get(ubicacion, 0) + delta
                if valor < 0:
                    raise ValueError("la reversión dejaría un saldo negativo")
                nuevos[ubicacion] = valor

            self._saldos.update(nuevos)
            self._revertidos.add(original)
            self._registrar(
                id, firma, "reversion", mov["destino"], mov["origen"], cantidad, original
            )
        return None
