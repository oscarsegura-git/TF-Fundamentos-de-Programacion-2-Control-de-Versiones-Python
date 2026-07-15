from comun import entrada
from comun.excepciones import EntregaNoDisponibleError, PedidoNoEncontradoError
from entregas.entrega import MODALIDAD_RECOJO, MODALIDAD_DELIVERY

class MenuEntregas:
    def __init__(self, gestor_entregas):
        self.__gestor = gestor_entregas

    def mostrar(self):
        opcion = ""
        while opcion != "3":
            entrada.titulo("Gestión de Entregas")
            print("  1. Entrega interna (Lima)")
            print("  2. Entrega externa (Provincias)")
            print("  3. Volver al menú principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3"])
            if opcion == "1":
                self._interna()
            elif opcion == "2":
                self._externa()

    def _cargar_pedido(self):
        codigo = entrada.pedir_texto(" Código de pedido      : ")
        try:
            pedido = self.__gestor.cargar_pedido(codigo)
        except (PedidoNoEncontradoError, EntregaNoDisponibleError) as error:
            print(entrada.linea())
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return None
        print(" [OK] Pedido disponible para entrega (estado: " + pedido.estado +
              "). Cliente: " + pedido.cliente.nombre)
        print(entrada.linea())
        return pedido

    def _interna(self):
        entrada.titulo("Entrega interna")
        pedido = self._cargar_pedido()
        if pedido is None:
            return
        if not self.__gestor.esta_en_cobertura(pedido.cliente):
            print(" [INFO] El cliente está FUERA de la zona de cobertura.")
            print("        Se redirige a ENTREGA EXTERNA.")
            self._externa(pedido)
            return
        motorizado = entrada.pedir_texto(" Nombre del motorizado : ")
        placa = entrada.pedir_texto(" Placa                 : ")
        tipo_placa = entrada.pedir_texto(" Tipo de placa         : ")
        hora_salida = entrada.pedir_fecha(" Hora de salida        : ")
        hora_entrega = entrada.pedir_fecha(" Hora est. de entrega  : ")
        try:
            entrega = self.__gestor.asignar_interna(
                pedido, motorizado, placa, tipo_placa, hora_salida, hora_entrega)
        except EntregaNoDisponibleError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        self._mostrar_comprobante("Código QR generado", entrega, pedido)

    def _externa(self, pedido=None):
        if pedido is None:
            entrada.titulo("Entrega externa")
            pedido = self._cargar_pedido()
            if pedido is None:
                return
        print(" Modalidad:")
        print("   1. Recojo en tienda")
        print("   2. Delivery por paquetería")
        opcion = entrada.pedir_opcion(" Opción: ", ["1", "2"])
        print(entrada.linea())
        try:
            if opcion == "1":
                entrega = self.__gestor.asignar_externa(pedido, MODALIDAD_RECOJO)
            else:
                entrega = self._asignar_delivery(pedido)
        except EntregaNoDisponibleError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        self._mostrar_comprobante("Rotulado generado", entrega, pedido)

    def _asignar_delivery(self, pedido):
        sede_origen = entrada.pedir_texto(" Sede de origen          : ")
        destino = entrada.pedir_texto(" Destino                 : ")
        remitente_nombre = entrada.pedir_texto(" Nombre del remitente    : ")
        remitente_doc = entrada.pedir_texto(" DNI/RUC del remitente   : ")
        destinatario_nombre = entrada.pedir_texto(" Nombre del destinatario : ")
        destinatario_doc = entrada.pedir_texto(" DNI del destinatario    : ")
        direccion = entrada.pedir_texto(" Dirección de entrega    : ")
        courier = entrada.pedir_texto(" Empresa de paquetería   : ")
        return self.__gestor.asignar_externa(
            pedido, MODALIDAD_DELIVERY, sede_origen, destino, remitente_nombre,
            remitente_doc, destinatario_nombre, destinatario_doc, direccion,
            courier)

    def _mostrar_comprobante(self, titulo, entrega, pedido):
        print(entrada.linea())
        print(" " + titulo.upper())
        print(entrada.linea())
        for linea in entrega.comprobante_texto.strip().split("\n"):
            print("  " + linea)
        print("  [Archivo generado: " + entrega.comprobante_archivo + "]")
        print(entrada.linea())
        print(" [OK] Estado actualizado a \"" + pedido.estado + "\".")
        entrada.pausar()
