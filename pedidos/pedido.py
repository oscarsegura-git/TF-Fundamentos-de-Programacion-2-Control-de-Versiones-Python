from datetime import datetime

from comun.excepciones import DatoInvalidoError, TransicionInvalidaError

PENDIENTE = "Pendiente de pago"
COMPRADO = "Comprado"
EN_TRANSITO = "En tránsito"
EN_ALMACEN = "En almacén"
EN_CAMINO = "En camino"
ENTREGADO = "Entregado"
LISTO_RECOJO = "Listo para recojo"
CANCELADO = "Cancelado"

ESTADOS = [PENDIENTE, COMPRADO, EN_TRANSITO, EN_ALMACEN, EN_CAMINO,
           LISTO_RECOJO, ENTREGADO, CANCELADO]

TRANSICIONES = [
    [PENDIENTE, [COMPRADO, CANCELADO]],
    [COMPRADO, [EN_TRANSITO, EN_CAMINO, LISTO_RECOJO, CANCELADO]],
    [EN_TRANSITO, [EN_ALMACEN]],
    [EN_ALMACEN, [EN_CAMINO, LISTO_RECOJO]],
    [EN_CAMINO, [ENTREGADO]],
    [LISTO_RECOJO, [ENTREGADO]],
    [ENTREGADO, []],
    [CANCELADO, []],
]

MEDIOS_PAGO = ["Efectivo", "Tarjeta", "Yape / Plin", "Transferencia"]

def siguientes_de(estado):
    for fila in TRANSICIONES:
        if fila[0] == estado:
            return list(fila[1])
    return []

class CambioEstado:
    def __init__(self, estado, fecha_hora):
        self.__estado = estado
        self.__fecha_hora = fecha_hora

    @property
    def estado(self):
        return self.__estado

    @property
    def fecha_hora(self):
        return self.__fecha_hora

    def __str__(self):
        return self.__fecha_hora + " - " + self.__estado

class LineaPedido:
    def __init__(self, producto, cantidad):
        self.__producto = producto
        self.__cantidad = cantidad

    @property
    def producto(self):
        return self.__producto

    @property
    def cantidad(self):
        return self.__cantidad

    def subtotal(self):
        return self.__producto.precio * self.__cantidad

class Pedido:
    def __init__(self, codigo, cliente, tipo_prenda, cantidad, peso):
        self.__codigo = str(codigo).strip().upper()
        self.__cliente = cliente
        self.tipo_prenda = tipo_prenda
        self.cantidad = cantidad
        self.peso = peso
        self.__lineas = []
        self.__entrega = None
        self.__estado = PENDIENTE
        self.__fecha_registro = datetime.now()
        self.__historial = [CambioEstado(PENDIENTE, self._ahora())]
        self.__metodo_pago = None
        self.__monto_pagado = None
        self.__fecha_pago = None

    def _ahora(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    @property
    def codigo(self):
        return self.__codigo

    @property
    def cliente(self):
        return self.__cliente

    @property
    def fecha_registro(self):
        return self.__fecha_registro

    @property
    def tipo_prenda(self):
        return self.__tipo_prenda

    @tipo_prenda.setter
    def tipo_prenda(self, valor):
        valor = str(valor).strip()
        if valor == "":
            raise DatoInvalidoError("El campo tipo de prenda no puede estar vacío.")
        self.__tipo_prenda = valor

    @property
    def cantidad(self):
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if valor <= 0:
            raise DatoInvalidoError("La cantidad debe ser mayor que cero.")
        self.__cantidad = int(valor)

    @property
    def peso(self):
        return self.__peso

    @peso.setter
    def peso(self, valor):
        if valor <= 0:
            raise DatoInvalidoError("El peso debe ser mayor que cero.")
        self.__peso = float(valor)

    @property
    def estado(self):
        return self.__estado

    @property
    def entrega(self):
        return self.__entrega

    @property
    def metodo_pago(self):
        return self.__metodo_pago

    @property
    def monto_pagado(self):
        return self.__monto_pagado

    @property
    def fecha_pago(self):
        return self.__fecha_pago

    @property
    def historial(self):
        return list(self.__historial)

    @property
    def lineas(self):
        return list(self.__lineas)

    def ultima_actualizacion(self):
        return self.__historial[-1].fecha_hora

    def estados_siguientes(self):
        return siguientes_de(self.__estado)

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in siguientes_de(self.__estado):
            raise TransicionInvalidaError(
                "No se puede pasar de '" + self.__estado + "' a '" +
                nuevo_estado + "'.")
        self.__estado = nuevo_estado
        self.__historial.append(CambioEstado(nuevo_estado, self._ahora()))

    def registrar_pago(self, metodo_pago, monto):
        metodo_pago = str(metodo_pago).strip()
        if metodo_pago == "":
            raise DatoInvalidoError("Debe indicar el medio de pago.")
        try:
            monto = float(monto)
        except (TypeError, ValueError):
            raise DatoInvalidoError("El monto pagado no es válido.")
        if monto < 0:
            raise DatoInvalidoError("El monto pagado no puede ser negativo.")
        self.cambiar_estado(COMPRADO)
        self.__metodo_pago = metodo_pago
        self.__monto_pagado = monto
        self.__fecha_pago = self._ahora()

    def asignar_entrega(self, entrega):
        if self.__entrega is not None:
            raise TransicionInvalidaError("El pedido ya tiene una entrega asignada.")
        self.__entrega = entrega

    def agregar_linea(self, producto, cantidad):
        self.__lineas.append(LineaPedido(producto, cantidad))

    def total_productos(self):
        return sum(linea.subtotal() for linea in self.__lineas)

    def coincide(self, texto):
        texto = str(texto).strip().lower()
        return (texto == self.__codigo.lower()
                or texto == self.__cliente.dni
                or texto in self.__cliente.nombre.lower())

    def __str__(self):
        return self.__codigo + " | " + self.__cliente.nombre + " | " + self.__estado

    def _a_dict(self):
        return {
            "codigo": self.__codigo,
            "cliente_dni": self.__cliente.dni,
            "tipo_prenda": self.__tipo_prenda,
            "cantidad": self.__cantidad,
            "peso": self.__peso,
            "estado": self.__estado,
            "fecha_registro": self.__fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
            "historial": [{"estado": h.estado, "fecha_hora": h.fecha_hora}
                          for h in self.__historial],
            "lineas": [{"codigo_producto": l.producto.codigo, "cantidad": l.cantidad}
                      for l in self.__lineas],
            "metodo_pago": self.__metodo_pago,
            "monto_pagado": self.__monto_pagado,
            "fecha_pago": self.__fecha_pago,
            "entrega": self.__entrega._a_dict() if self.__entrega is not None else None,
        }

    @classmethod
    def _desde_dict(cls, data, cliente, buscador_productos):
        pedido = cls.__new__(cls)
        pedido.__codigo = data["codigo"]
        pedido.__cliente = cliente
        pedido.tipo_prenda = data["tipo_prenda"]
        pedido.cantidad = data["cantidad"]
        pedido.peso = data["peso"]
        pedido.__lineas = []
        for linea in data.get("lineas", []):
            try:
                producto = buscador_productos(linea["codigo_producto"])
                pedido.__lineas.append(LineaPedido(producto, linea["cantidad"]))
            except Exception:
                pass
        pedido.__entrega = None
        pedido.__estado = data["estado"]
        pedido.__fecha_registro = datetime.strptime(
            data["fecha_registro"], "%Y-%m-%d %H:%M:%S")
        pedido.__historial = [CambioEstado(h["estado"], h["fecha_hora"])
                              for h in data["historial"]]
        pedido.__metodo_pago = data.get("metodo_pago")
        pedido.__monto_pagado = data.get("monto_pagado")
        pedido.__fecha_pago = data.get("fecha_pago")
        return pedido
