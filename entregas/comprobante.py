from abc import ABC, abstractmethod

from comun import recursos

SEPARADOR = "-" * 40

class Comprobante(ABC):
    @abstractmethod
    def generar(self, pedido, entrega):
        pass

class ComprobanteQR(Comprobante):
    def generar(self, pedido, entrega):
        cliente = pedido.cliente
        contenido = (
            "TENDENCIAS SHEIN PERÚ - ENTREGA INTERNA\n"
            "Cliente      : " + cliente.nombre + "\n"
            "Código cliente: " + cliente.dni + "\n"
            "Dirección    : " + cliente.direccion_completa() + "\n"
            "Teléfono     : " + cliente.telefono + "\n"
            "Pedido       : " + pedido.codigo + "\n"
            "Peso         : " + str(entrega.peso) + " kg\n"
            "Motorizado   : " + entrega.motorizado +
            " | Placa: " + entrega.placa + " (" + entrega.tipo_placa + ")\n"
            "Salida       : " + entrega.hora_salida + "\n"
            "Entrega est. : " + entrega.hora_entrega + "\n"
        )
        ruta = recursos.generar_qr(contenido, "qr_" + pedido.codigo)
        return contenido, ruta

class ComprobanteRotulado(Comprobante):
    def generar(self, pedido, entrega):
        if entrega.es_recojo():
            texto = self._rotulado_recojo(pedido, entrega)
        else:
            texto = self._rotulado_delivery(pedido, entrega)
        ruta = recursos.generar_rotulado_imagen(texto, "rotulado_" + pedido.codigo)
        return texto, ruta

    def _rotulado_recojo(self, pedido, entrega):
        return (
            "TENDENCIAS SHEIN PERÚ\n"
            "ROTULADO - RECOJO EN TIENDA\n"
            + SEPARADOR + "\n"
            "Pedido    : " + pedido.codigo + "\n"
            "Cliente   : " + pedido.cliente.nombre + "\n"
            "Modalidad : " + entrega.modalidad_texto() + "\n"
            "Peso      : " + str(entrega.peso) + " kg\n"
        )

    def _rotulado_delivery(self, pedido, entrega):
        return (
            "TENDENCIAS SHEIN PERÚ\n"
            "Pedido: " + pedido.codigo + "\n"
            + SEPARADOR + "\n"
            "Remitente   : " + entrega.remitente_nombre + "\n"
            "DNI/RUC     : " + entrega.remitente_doc + "\n"
            "Origen      : " + entrega.sede_origen + "\n"
            + SEPARADOR + "\n"
            "Destinatario: " + entrega.destinatario_nombre + "\n"
            "DNI         : " + entrega.destinatario_doc + "\n"
            "Dirección   : " + entrega.direccion + "\n"
            "Destino     : " + entrega.destino + "\n"
            + SEPARADOR + "\n"
            "Courier     : " + entrega.courier + "\n"
            "Peso        : " + str(entrega.peso) + " kg\n"
        )
