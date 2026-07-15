from entregas.entrega import EntregaInterna, EntregaExterna
from pedidos.pedido import COMPRADO, EN_ALMACEN
from comun.excepciones import EntregaNoDisponibleError

DISTRITOS_COBERTURA = [
    "san juan de lurigancho", "sjl", "los olivos", "san martín de porres",
    "san martin de porres", "smp", "comas", "cercado de lima", "lima",
    "la victoria", "ate", "santa anita", "surco", "san borja", "miraflores",
    "surquillo",
]

ESTADOS_DISPONIBLES_ENTREGA = [COMPRADO, EN_ALMACEN]

class GestorEntregas:
    def __init__(self, gestor_pedidos):
        self.__gestor_pedidos = gestor_pedidos

    def cargar_pedido(self, codigo):
        pedido = self.__gestor_pedidos.buscar_por_codigo(codigo)
        self.verificar_disponible(pedido)
        return pedido

    def verificar_disponible(self, pedido):
        if pedido.estado not in ESTADOS_DISPONIBLES_ENTREGA:
            raise EntregaNoDisponibleError(
                "El pedido no está disponible para entrega "
                "(estado actual: " + pedido.estado + "). Debe estar \"" +
                COMPRADO + "\" o \"" + EN_ALMACEN + "\".")

    def esta_en_cobertura(self, cliente):
        ciudad = cliente.ciudad.strip().lower()
        distrito = cliente.distrito.strip().lower()
        return ciudad == "lima" and distrito in DISTRITOS_COBERTURA

    def _confirmar(self, pedido, entrega):
        pedido.asignar_entrega(entrega)
        entrega.generar_comprobante(pedido)
        pedido.cambiar_estado(entrega.estado_resultante())
        return entrega

    def asignar_interna(self, pedido, motorizado, placa, tipo_placa,
                        hora_salida, hora_entrega):
        self.verificar_disponible(pedido)
        if not self.esta_en_cobertura(pedido.cliente):
            raise EntregaNoDisponibleError(
                "El cliente está fuera de la zona de cobertura; "
                "corresponde entrega externa.")
        entrega = EntregaInterna(pedido.peso, motorizado, placa, tipo_placa,
                                 hora_salida, hora_entrega)
        return self._confirmar(pedido, entrega)

    def asignar_externa(self, pedido, modalidad, sede_origen="", destino="",
                        remitente_nombre="", remitente_doc="",
                        destinatario_nombre="", destinatario_doc="",
                        direccion="", courier=""):
        self.verificar_disponible(pedido)
        entrega = EntregaExterna(pedido.peso, modalidad, sede_origen, destino,
                                 remitente_nombre, remitente_doc,
                                 destinatario_nombre, destinatario_doc,
                                 direccion, courier)
        return self._confirmar(pedido, entrega)
