"""Libro de inventario con movimientos idempotentes y reversibles."""

INGRESO = "ingreso"
RETIRO = "retiro"
TRANSFERENCIA = "transferencia"
REVERSION = "reversion"


def _texto(valor, descripcion):
    """Devuelve ``valor`` como ``str`` exacto si es un string no vacío."""
    if isinstance(valor, str):
        # Copia como str exacto: descarta comportamientos de subclases.
        valor = str.__str__(valor)
        if valor:
            return valor
    raise ValueError(f"{descripcion} debe ser un string no vacío")


def _cantidad(valor):
    """Devuelve ``valor`` como ``int`` exacto si es un entero positivo no booleano."""
    if isinstance(valor, int) and not isinstance(valor, bool):
        valor = int.__index__(valor)
        if valor > 0:
            return valor
    raise ValueError("la cantidad debe ser un entero positivo (no booleano)")


class Inventario:
    """Saldos por ubicación más el historial de movimientos aplicados.

    Cada operación valida todo antes de modificar el estado: una excepción
    nunca deja efectos parciales ni consume el identificador del intento.
    """

    def __init__(self):
        self._saldos = {}      # ubicación -> unidades
        self._historial = []   # movimientos en orden de aplicación
        self._aplicados = {}   # id -> (firma de la llamada, movimiento)
        self._revertidos = {}  # id original -> id de su reversión

    def saldo(self, ubicacion):
        return self._saldos.get(_texto(ubicacion, "la ubicación"), 0)

    def historial(self):
        return [dict(movimiento) for movimiento in self._historial]

    def ingresar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        firma = ("ingresar", ubicacion, cantidad)
        if not self._ya_aplicado(id, firma):
            self._aplicar(id, firma, INGRESO, None, ubicacion, cantidad, None)

    def retirar(self, id, ubicacion, cantidad):
        id = _texto(id, "el identificador")
        ubicacion = _texto(ubicacion, "la ubicación")
        cantidad = _cantidad(cantidad)
        firma = ("retirar", ubicacion, cantidad)
        if not self._ya_aplicado(id, firma):
            self._aplicar(id, firma, RETIRO, ubicacion, None, cantidad, None)

    def transferir(self, id, origen, destino, cantidad):
        id = _texto(id, "el identificador")
        origen = _texto(origen, "el origen")
        destino = _texto(destino, "el destino")
        cantidad = _cantidad(cantidad)
        if origen == destino:
            raise ValueError("el origen y el destino deben ser distintos")
        firma = ("transferir", origen, destino, cantidad)
        if not self._ya_aplicado(id, firma):
            self._aplicar(id, firma, TRANSFERENCIA, origen, destino, cantidad, None)

    def revertir(self, id, original):
        id = _texto(id, "el identificador")
        original = _texto(original, "el identificador original")
        firma = ("revertir", original)
        if self._ya_aplicado(id, firma):
            return
        if original not in self._aplicados:
            raise ValueError(f"no existe el movimiento {original!r}")
        _, movimiento = self._aplicados[original]
        if movimiento["tipo"] == REVERSION:
            raise ValueError(f"{original!r} es una reversión y no se puede revertir")
        if original in self._revertidos:
            raise ValueError(
                f"el movimiento {original!r} ya fue revertido por "
                f"{self._revertidos[original]!r}"
            )
        # Intercambiar origen y destino deshace exactamente sus variaciones.
        self._aplicar(
            id,
            firma,
            REVERSION,
            movimiento["destino"],
            movimiento["origen"],
            movimiento["cantidad"],
            original,
        )

    def _ya_aplicado(self, identificador, firma):
        """True si la llamada repite una ya aplicada (no hay que hacer nada).

        Lanza ``ValueError`` si el identificador se usó con otra operación o
        con otros argumentos.
        """
        aplicado = self._aplicados.get(identificador)
        if aplicado is None:
            return False
        if aplicado[0] != firma:
            raise ValueError(
                f"el identificador {identificador!r} ya se usó con otra "
                "operación o argumentos"
            )
        return True

    def _aplicar(self, identificador, firma, tipo, origen, destino, cantidad, original):
        """Resta de ``origen`` y suma a ``destino`` (``None`` = afuera del libro).

        Calcula y valida los saldos resultantes antes de tocar el estado; si
        alguno quedaría negativo lanza ``ValueError`` sin efectos.
        """
        nuevos_saldos = {}
        if origen is not None:
            disponible = self._saldos.get(origen, 0)
            if disponible < cantidad:
                raise ValueError(
                    f"saldo insuficiente en {origen!r}: hay {disponible}, "
                    f"se requieren {cantidad}"
                )
            nuevos_saldos[origen] = disponible - cantidad
        if destino is not None:
            nuevos_saldos[destino] = self._saldos.get(destino, 0) + cantidad
        movimiento = {
            "id": identificador,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }
        # Sin validaciones pendientes: se confirma todo junto.
        self._saldos.update(nuevos_saldos)
        self._historial.append(movimiento)
        self._aplicados[identificador] = (firma, movimiento)
        if original is not None:
            self._revertidos[original] = identificador
