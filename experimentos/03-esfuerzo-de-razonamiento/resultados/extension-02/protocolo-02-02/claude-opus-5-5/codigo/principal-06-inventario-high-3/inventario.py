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
        # id -> (firma, registro)
        self._movimientos = {}
        # ids de movimientos ya revertidos
        self._revertidos = set()

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "ubicacion")
        return self._saldos.get(ubicacion, 0)

    def historial(self):
        return [dict(registro) for registro in self._historial]

    # ------------------------------------------------------------------ #
    # Auxiliares
    # ------------------------------------------------------------------ #
    def _ya_aplicado(self, id_mov, firma):
        """True si el id ya existe con la misma firma; ValueError si difiere."""
        existente = self._movimientos.get(id_mov)
        if existente is None:
            return False
        if existente[0] != firma:
            raise ValueError(f"el identificador {id_mov!r} ya fue usado con otros argumentos")
        return True

    def _aplicar(self, id_mov, firma, cambios, registro):
        """Valida y aplica atómicamente variaciones de saldo y registra el movimiento."""
        nuevos = {}
        for ubicacion, delta in cambios:
            nuevos[ubicacion] = nuevos.get(ubicacion, self._saldos.get(ubicacion, 0)) + delta
        for ubicacion, valor in nuevos.items():
            if valor < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")
        self._saldos.update(nuevos)
        self._movimientos[id_mov] = (firma, registro)
        self._historial.append(registro)

    @staticmethod
    def _registro(id_mov, tipo, origen, destino, cantidad, original=None):
        return {
            "id": id_mov,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    # ------------------------------------------------------------------ #
    # Mutaciones
    # ------------------------------------------------------------------ #
    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("ingreso", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        registro = self._registro(id, "ingreso", None, ubicacion, cantidad)
        self._aplicar(id, firma, [(ubicacion, cantidad)], registro)
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "id")
        _validar_texto(ubicacion, "ubicacion")
        _validar_cantidad(cantidad)
        firma = ("retiro", ubicacion, cantidad)
        if self._ya_aplicado(id, firma):
            return None
        registro = self._registro(id, "retiro", ubicacion, None, cantidad)
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
        if self._ya_aplicado(id, firma):
            return None
        registro = self._registro(id, "transferencia", origen, destino, cantidad)
        self._aplicar(id, firma, [(origen, -cantidad), (destino, cantidad)], registro)
        return None

    def revertir(self, id, original):
        _validar_texto(id, "id")
        _validar_texto(original, "original")
        firma = ("reversion", original)
        if self._ya_aplicado(id, firma):
            return None
        existente = self._movimientos.get(original)
        if existente is None:
            raise ValueError(f"no existe el movimiento {original!r}")
        mov = existente[1]
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")

        cantidad = mov["cantidad"]
        cambios = []
        if mov["destino"] is not None:
            cambios.append((mov["destino"], -cantidad))
        if mov["origen"] is not None:
            cambios.append((mov["origen"], cantidad))

        registro = self._registro(
            id, "reversion", mov["destino"], mov["origen"], cantidad, original
        )
        self._aplicar(id, firma, cambios, registro)
        self._revertidos.add(original)
        return None
