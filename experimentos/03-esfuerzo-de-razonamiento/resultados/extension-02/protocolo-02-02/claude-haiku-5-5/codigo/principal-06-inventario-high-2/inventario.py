"""Implementá el libro de inventario pedido en TAREA.md."""


class Inventario:
    def __init__(self):
        self._saldos = {}
        self._movimientos = {}
        self._historial = []
        self._revertidos = set()

    @staticmethod
    def _validar_texto(valor, nombre):
        if not isinstance(valor, str) or valor == "":
            raise ValueError(f"{nombre} debe ser un string no vacío")
        return valor

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("la cantidad debe ser un entero positivo")
        return cantidad

    @staticmethod
    def _entrada(id_, tipo, origen, destino, cantidad, original):
        return {
            "id": id_,
            "tipo": tipo,
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad,
            "original": original,
        }

    @staticmethod
    def _firma(entrada):
        return (
            entrada["tipo"],
            entrada["origen"],
            entrada["destino"],
            entrada["cantidad"],
            entrada["original"],
        )

    def _ya_registrado(self, entrada):
        previa = self._movimientos.get(entrada["id"])
        if previa is None:
            return False
        if self._firma(previa) != self._firma(entrada):
            raise ValueError(
                f"el identificador {entrada['id']!r} ya se usó con otros argumentos"
            )
        return True

    def _nuevos_saldos(self, origen, destino, cantidad):
        nuevos = {}
        if origen is not None:
            nuevos[origen] = self._saldos.get(origen, 0) - cantidad
        if destino is not None:
            nuevos[destino] = self._saldos.get(destino, 0) + cantidad
        if any(s < 0 for s in nuevos.values()):
            raise ValueError("el saldo quedaría negativo o es insuficiente")
        return nuevos

    def _confirmar(self, entrada):
        nuevos = self._nuevos_saldos(entrada["origen"], entrada["destino"], entrada["cantidad"])
        self._saldos.update(nuevos)
        self._movimientos[entrada["id"]] = entrada
        self._historial.append(dict(entrada))
        if entrada["tipo"] == "reversion":
            self._revertidos.add(entrada["original"])

    def saldo(self, ubicacion):
        ubicacion = self._validar_texto(ubicacion, "la ubicación")
        return self._saldos.get(ubicacion, 0)

    def ingresar(self, id, ubicacion, cantidad):
        id_ = self._validar_texto(id, "el identificador")
        ubicacion = self._validar_texto(ubicacion, "la ubicación")
        cantidad = self._validar_cantidad(cantidad)
        entrada = self._entrada(id_, "ingreso", None, ubicacion, cantidad, None)
        if not self._ya_registrado(entrada):
            self._confirmar(entrada)

    def retirar(self, id, ubicacion, cantidad):
        id_ = self._validar_texto(id, "el identificador")
        ubicacion = self._validar_texto(ubicacion, "la ubicación")
        cantidad = self._validar_cantidad(cantidad)
        entrada = self._entrada(id_, "retiro", ubicacion, None, cantidad, None)
        if not self._ya_registrado(entrada):
            self._confirmar(entrada)

    def transferir(self, id, origen, destino, cantidad):
        id_ = self._validar_texto(id, "el identificador")
        origen = self._validar_texto(origen, "la ubicación de origen")
        destino = self._validar_texto(destino, "la ubicación de destino")
        cantidad = self._validar_cantidad(cantidad)
        if origen == destino:
            raise ValueError("origen y destino deben ser distintos")
        entrada = self._entrada(id_, "transferencia", origen, destino, cantidad, None)
        if not self._ya_registrado(entrada):
            self._confirmar(entrada)

    def revertir(self, id, original):
        id_ = self._validar_texto(id, "el identificador")
        original = self._validar_texto(original, "el identificador original")
        mov = self._movimientos.get(original)
        if mov is None:
            raise ValueError(f"movimiento original {original!r} inexistente")
        if mov["tipo"] == "reversion":
            raise ValueError("no se puede revertir una reversión")
        entrada = self._entrada(
            id_, "reversion", mov["destino"], mov["origen"], mov["cantidad"], original
        )
        if self._ya_registrado(entrada):
            return
        if original in self._revertidos:
            raise ValueError(f"el movimiento {original!r} ya fue revertido")
        self._confirmar(entrada)

    def historial(self):
        return [dict(e) for e in self._historial]
