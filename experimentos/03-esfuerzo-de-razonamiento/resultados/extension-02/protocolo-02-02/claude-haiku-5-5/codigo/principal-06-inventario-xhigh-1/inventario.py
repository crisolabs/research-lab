"""Implementá el libro de inventario pedido en TAREA.md."""


def _texto(valor):
    if not isinstance(valor, str) or valor == "":
        raise ValueError("se requiere un string no vacío")
    return valor


def _cantidad(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ValueError("la cantidad debe ser un entero positivo")
    return valor


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = []
        self._por_id = {}
        self._revertidos = set()

    def saldo(self, ubicacion):
        _texto(ubicacion)
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        _texto(id)
        _texto(ubicacion)
        _cantidad(cantidad)
        self._operar({
            "id": id, "tipo": "ingreso", "origen": None,
            "destino": ubicacion, "cantidad": cantidad, "original": None,
        })

    def retirar(self, id, ubicacion, cantidad):
        _texto(id)
        _texto(ubicacion)
        _cantidad(cantidad)
        self._operar({
            "id": id, "tipo": "retiro", "origen": ubicacion,
            "destino": None, "cantidad": cantidad, "original": None,
        })

    def transferir(self, id, origen, destino, cantidad):
        _texto(id)
        _texto(origen)
        _texto(destino)
        _cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        self._operar({
            "id": id, "tipo": "transferencia", "origen": origen,
            "destino": destino, "cantidad": cantidad, "original": None,
        })

    def revertir(self, id, original):
        _texto(id)
        _texto(original)
        previo = self._por_id.get(id)
        if previo is not None:
            if previo["tipo"] == "reversion" and previo["original"] == original:
                return
            raise ValueError("identificador ya utilizado con otros argumentos")
        mov = self._por_id.get(original)
        if mov is None:
            raise ValueError("movimiento original inexistente")
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        if original in self._revertidos:
            raise ValueError("el movimiento ya fue revertido")
        registro = {
            "id": id, "tipo": "reversion", "origen": mov["destino"],
            "destino": mov["origen"], "cantidad": mov["cantidad"],
            "original": original,
        }
        self._mover(registro["origen"], registro["destino"], registro["cantidad"])
        self._revertidos.add(original)
        self._guardar(registro)

    def historial(self):
        return [dict(m) for m in self._movimientos]

    def _operar(self, registro):
        previo = self._por_id.get(registro["id"])
        if previo is not None:
            if previo != registro:
                raise ValueError("identificador ya utilizado con otros argumentos")
            return
        self._mover(registro["origen"], registro["destino"], registro["cantidad"])
        self._guardar(registro)

    def _mover(self, origen, destino, cantidad):
        if origen is not None and self._saldos.get(origen, 0) < cantidad:
            raise ValueError("saldo insuficiente")
        if origen is not None:
            self._saldos[origen] = self._saldos.get(origen, 0) - cantidad
        if destino is not None:
            self._saldos[destino] = self._saldos.get(destino, 0) + cantidad

    def _guardar(self, registro):
        self._movimientos.append(registro)
        self._por_id[registro["id"]] = registro
