from abc import ABC, abstractmethod

from entregas.comprobante import ComprobanteQR, ComprobanteRotulado
from pedidos.pedido import EN_CAMINO, LISTO_RECOJO

MODALIDAD_RECOJO = "recojo"
MODALIDAD_DELIVERY = "delivery"

class Entrega(ABC):
    __IGV = 0.18

    def __init__(self, peso):
        self.__peso = float(peso)
        self.__comprobante_texto = None
        self.__comprobante_archivo = None

    @property
    def peso(self):
        return self.__peso

    @property
    def comprobante_texto(self):
        return self.__comprobante_texto

    @property
    def comprobante_archivo(self):
        return self.__comprobante_archivo

    @abstractmethod
    def tarifa_base(self):
        pass

    @abstractmethod
    def tarifa_por_kg(self):
        pass

    @abstractmethod
    def nombre_tipo(self):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    @abstractmethod
    def estado_resultante(self):
        pass

    @abstractmethod
    def crear_comprobante(self):
        pass

    def calcular_costo(self):
        return self.tarifa_base() + self.tarifa_por_kg() * self.__peso

    def desglose(self):
        subtotal = self.calcular_costo()
        igv = subtotal * self.__IGV
        return subtotal, igv, subtotal + igv

    def generar_comprobante(self, pedido):
        comprobante = self.crear_comprobante()
        texto, ruta = comprobante.generar(pedido, self)
        self.__comprobante_texto = texto
        self.__comprobante_archivo = ruta
        return texto, ruta

    def _restaurar_comprobante(self, texto, ruta):
        self.__comprobante_texto = texto
        self.__comprobante_archivo = ruta

class EntregaInterna(Entrega):
    __TARIFA_BASE = 5.00
    __TARIFA_KG = 3.00

    def __init__(self, peso, motorizado, placa, tipo_placa, hora_salida, hora_entrega):
        super().__init__(peso)
        self.__motorizado = motorizado
        self.__placa = placa
        self.__tipo_placa = tipo_placa
        self.__hora_salida = hora_salida
        self.__hora_entrega = hora_entrega

    @property
    def motorizado(self):
        return self.__motorizado

    @property
    def placa(self):
        return self.__placa

    @property
    def tipo_placa(self):
        return self.__tipo_placa

    @property
    def hora_salida(self):
        return self.__hora_salida

    @property
    def hora_entrega(self):
        return self.__hora_entrega

    def tarifa_base(self):
        return self.__TARIFA_BASE

    def tarifa_por_kg(self):
        return self.__TARIFA_KG

    def nombre_tipo(self):
        return "Entrega interna"

    def descripcion(self):
        return "Entrega interna (motorizado, QR)"

    def estado_resultante(self):
        return EN_CAMINO

    def crear_comprobante(self):
        return ComprobanteQR()

    def _a_dict(self):
        return {
            "tipo": "interna",
            "peso": self.peso,
            "motorizado": self.__motorizado,
            "placa": self.__placa,
            "tipo_placa": self.__tipo_placa,
            "hora_salida": self.__hora_salida,
            "hora_entrega": self.__hora_entrega,
            "comprobante_texto": self.comprobante_texto,
            "comprobante_archivo": self.comprobante_archivo,
        }

    @classmethod
    def _desde_dict(cls, data):
        entrega = cls(data["peso"], data["motorizado"], data["placa"],
                      data["tipo_placa"], data["hora_salida"], data["hora_entrega"])
        entrega._restaurar_comprobante(data.get("comprobante_texto"),
                                       data.get("comprobante_archivo"))
        return entrega

class EntregaExterna(Entrega):
    __TARIFA_BASE_RECOJO = 8.00
    __TARIFA_KG_RECOJO = 1.50
    __TARIFA_BASE_DELIVERY = 12.00
    __TARIFA_KG_DELIVERY = 3.50

    def __init__(self, peso, modalidad, sede_origen="", destino="",
                 remitente_nombre="", remitente_doc="", destinatario_nombre="",
                 destinatario_doc="", direccion="", courier=""):
        super().__init__(peso)
        self.__modalidad = modalidad
        self.__sede_origen = sede_origen
        self.__destino = destino
        self.__remitente_nombre = remitente_nombre
        self.__remitente_doc = remitente_doc
        self.__destinatario_nombre = destinatario_nombre
        self.__destinatario_doc = destinatario_doc
        self.__direccion = direccion
        self.__courier = courier

    @property
    def modalidad(self):
        return self.__modalidad

    @property
    def sede_origen(self):
        return self.__sede_origen

    @property
    def destino(self):
        return self.__destino

    @property
    def remitente_nombre(self):
        return self.__remitente_nombre

    @property
    def remitente_doc(self):
        return self.__remitente_doc

    @property
    def destinatario_nombre(self):
        return self.__destinatario_nombre

    @property
    def destinatario_doc(self):
        return self.__destinatario_doc

    @property
    def direccion(self):
        return self.__direccion

    @property
    def courier(self):
        return self.__courier

    def es_recojo(self):
        return self.__modalidad == MODALIDAD_RECOJO

    def tarifa_base(self):
        return self.__TARIFA_BASE_RECOJO if self.es_recojo() else self.__TARIFA_BASE_DELIVERY

    def tarifa_por_kg(self):
        return self.__TARIFA_KG_RECOJO if self.es_recojo() else self.__TARIFA_KG_DELIVERY

    def modalidad_texto(self):
        return "Recojo en tienda" if self.es_recojo() else "Delivery por paquetería"

    def nombre_tipo(self):
        return "Entrega externa (" + self.modalidad_texto().lower() + ")"

    def descripcion(self):
        return "Entrega externa (" + self.modalidad_texto().lower() + ", rotulado)"

    def estado_resultante(self):
        return LISTO_RECOJO if self.es_recojo() else EN_CAMINO

    def crear_comprobante(self):
        return ComprobanteRotulado()

    def _a_dict(self):
        return {
            "tipo": "externa",
            "peso": self.peso,
            "modalidad": self.__modalidad,
            "sede_origen": self.__sede_origen,
            "destino": self.__destino,
            "remitente_nombre": self.__remitente_nombre,
            "remitente_doc": self.__remitente_doc,
            "destinatario_nombre": self.__destinatario_nombre,
            "destinatario_doc": self.__destinatario_doc,
            "direccion": self.__direccion,
            "courier": self.__courier,
            "comprobante_texto": self.comprobante_texto,
            "comprobante_archivo": self.comprobante_archivo,
        }

    @classmethod
    def _desde_dict(cls, data):
        entrega = cls(data["peso"], data["modalidad"], data.get("sede_origen", ""),
                      data.get("destino", ""), data.get("remitente_nombre", ""),
                      data.get("remitente_doc", ""), data.get("destinatario_nombre", ""),
                      data.get("destinatario_doc", ""), data.get("direccion", ""),
                      data.get("courier", ""))
        entrega._restaurar_comprobante(data.get("comprobante_texto"),
                                       data.get("comprobante_archivo"))
        return entrega

def entrega_desde_dict(data):
    if data is None:
        return None
    if data.get("tipo") == "interna":
        return EntregaInterna._desde_dict(data)
    return EntregaExterna._desde_dict(data)
