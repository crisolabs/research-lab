"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or not valor:
        raise ValueError(f"{nombre} debe ser un string no vacío")


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._historial = []
        self._movimientos = {}  # id -> registro (mismo objeto que en el historial)
        self._revertidos = set()  # ids de movimientos ya revertidos

    # ------------------------------------------------------------------ consultas

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(m) for m in self._historial]

    # ------------------------------------------------------------------ internos

    def _repetido(self, registro):
        """True si el id ya existe con la misma operación; ValueError si difiere."""
        previo = self._movimientos.get(registro["id"])
        if previo is None:
            return False
        if previo != registro:
            raise ValueError(
                f"el identificador {registro['id']!r} ya fue usado con otros argumentos"
            )
        return True

    def _aplicar(self, registro, variaciones):
        """Valida todas las variaciones y recién entonces las aplica."""
        nuevos = {}
        for ubicacion, delta in variaciones:
            base = nuevos.get(ubicacion, self._saldos.get(ubicacion, 0))
            nuevos[ubicacion] = base + delta
        for ubicacion, valor in nuevos.items():
            if valor < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")
        self._saldos.update(nuevos)
        self._historial.append(registro)
        self._movimientos[registro["id"]] = registro

    @staticmethod
    def _registro(id, tipo, origen, destino, cantidad, original=None):
        return {
            "id": id,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    @staticmethod
    def _variaciones(registro):
        variaciones = []
        if registro["origen"] is not None:
            variaciones.append((registro["origen"], -registro["cantidad"]))
        if registro["destino"] is not None:
            variaciones.append((registro["destino"], registro["cantidad"]))
        return variaciones

    def _mover(self, registro):
        if self._repetido(registro):
            return
        self._aplicar(registro, self._variaciones(registro))

    # ------------------------------------------------------------------ mutaciones

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._mover(self._registro(id, "ingreso", None, ubicacion, cantidad))

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        self._mover(self._registro(id, "retiro", ubicacion, None, cantidad))

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "el origen")
        _validar_texto(destino, "el destino")
        _validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._mover(self._registro(id, "transferencia", origen, destino, cantidad))

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        previo = self._movimientos.get(id)
        if previo is not None:
            if previo["tipo"] == "reversion" and previo["original"] == original:
                return
            raise ValueError(
                f"el identificador {id!r} ya fue usado con otros argumentos"
            )
        objetivo = self._movimientos.get(original)
        if objetivo is None:
            raise ValueError(f"no existe el movimiento {original!r}")
        if objetivo["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        registro = self._registro(
            id,
            "reversion",
            objetivo["destino"],
            objetivo["origen"],
            objetivo["cantidad"],
            original,
        )
        self._aplicar(registro, self._variaciones(registro))
        self._revertidos.add(original)
