"""Libro de inventario con movimientos idempotentes y reversiones."""


def _validar_texto(valor, nombre):
    if not isinstance(valor, str) or valor == "":
        raise ValueError(f"{nombre} debe ser un string no vacío")
    return valor


def _validar_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return cantidad


class Inventario:
    def __init__(self):
        self._saldos = {}
        # id -> (firma de la llamada, entrada del historial)
        self._registro = {}
        self._historial = []
        # ids de movimientos originales que ya fueron revertidos
        self._revertidos = set()

    # ----- utilidades internas -------------------------------------------

    def _es_repeticion(self, id_, firma):
        """True si el id ya se usó con la misma operación; ValueError si difiere."""
        previo = self._registro.get(id_)
        if previo is None:
            return False
        if previo[0] == firma:
            return True
        raise ValueError(f"identificador {id_!r} reutilizado con argumentos distintos")

    def _aplicar(self, id_, firma, entrada, marcar_revertido=None):
        """Valida los efectos sobre saldos y, si todo es válido, los aplica."""
        deltas = {}
        if entrada["origen"] is not None:
            deltas[entrada["origen"]] = deltas.get(entrada["origen"], 0) - entrada["cantidad"]
        if entrada["destino"] is not None:
            deltas[entrada["destino"]] = deltas.get(entrada["destino"], 0) + entrada["cantidad"]

        for ubicacion, delta in deltas.items():
            if self._saldos.get(ubicacion, 0) + delta < 0:
                raise ValueError(f"saldo insuficiente en {ubicacion!r}")

        for ubicacion, delta in deltas.items():
            self._saldos[ubicacion] = self._saldos.get(ubicacion, 0) + delta

        self._registro[id_] = (firma, entrada)
        self._historial.append(entrada)
        if marcar_revertido is not None:
            self._revertidos.add(marcar_revertido)

    @staticmethod
    def _entrada(id_, tipo, origen, destino, cantidad, original=None):
        return {
            "id": id_,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    # ----- API pública ----------------------------------------------------

    def saldo(self, ubicacion):
        _validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if self._es_repeticion(id, firma):
            return None
        entrada = self._entrada(id, "ingreso", None, ubicacion, cantidad)
        self._aplicar(id, firma, entrada)
        return None

    def retirar(self, id, ubicacion, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(ubicacion, "la ubicación")
        _validar_cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if self._es_repeticion(id, firma):
            return None
        entrada = self._entrada(id, "retiro", ubicacion, None, cantidad)
        self._aplicar(id, firma, entrada)
        return None

    def transferir(self, id, origen, destino, cantidad):
        _validar_texto(id, "el identificador")
        _validar_texto(origen, "la ubicación de origen")
        _validar_texto(destino, "la ubicación de destino")
        _validar_cantidad(cantidad)
        firma = ("transferir", origen, destino, cantidad)
        if self._es_repeticion(id, firma):
            return None
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        entrada = self._entrada(id, "transferencia", origen, destino, cantidad)
        self._aplicar(id, firma, entrada)
        return None

    def revertir(self, id, original):
        _validar_texto(id, "el identificador")
        _validar_texto(original, "el identificador original")
        firma = ("revertir", original)
        if self._es_repeticion(id, firma):
            return None

        movimiento = self._registro.get(original)
        if movimiento is None:
            raise ValueError(f"movimiento original {original!r} inexistente")
        _, orig = movimiento
        if orig["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")

        # La reversión invierte origen y destino y copia la cantidad.
        entrada = self._entrada(
            id,
            "reversion",
            orig["destino"],
            orig["origen"],
            orig["cantidad"],
            original,
        )
        self._aplicar(id, firma, entrada, marcar_revertido=original)
        return None

    def historial(self):
        return [dict(entrada) for entrada in self._historial]
