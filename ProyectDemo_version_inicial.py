from abc import ABC, abstractmethod
from barcode import Code128
from barcode.writer import ImageWriter
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from datetime import datetime, timedelta
import qrcode
from PIL import Image as PILImage, ImageDraw, ImageFont
import os


class DatoInvalidoError(Exception):
    pass


class PedidoNoEncontradoError(Exception):
    pass


class Cliente:
    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre


def cargar_fuente():
    try:
        return ImageFont.truetype("arial.ttf", 20)
    except:
        return ImageFont.load_default()


def crear_codigo_barras(codigo):
    nombre = "barcode_" + codigo
    codigo_barras = Code128(codigo, writer=ImageWriter())
    return codigo_barras.save(nombre)


class Comprobante(ABC):
    @abstractmethod
    def generar(self, pedido):
        pass


class ComprobanteQR(Comprobante):
    def generar(self, pedido):
        entrega = pedido.entrega
        inicio = datetime.strptime(entrega.fecha_hora, "%Y-%m-%d %H:%M")
        fin = inicio + timedelta(minutes=30)
        evento = "BEGIN:VCALENDAR\n"
        evento = evento + "VERSION:2.0\n"
        evento = evento + "BEGIN:VEVENT\n"
        evento = evento + "SUMMARY:Entrega Pedido Cliente " + pedido.cliente.nombre + "\n"
        evento = evento + "DESCRIPTION:Motorizado: " + entrega.motorizado + "; Placa: " + entrega.placa + "\n"
        evento = evento + "LOCATION:Tienda Central\n"
        evento = evento + "DTSTART:" + inicio.strftime("%Y%m%dT%H%M%S") + "\n"
        evento = evento + "DTEND:" + fin.strftime("%Y%m%dT%H%M%S") + "\n"
        evento = evento + "END:VEVENT\n"
        evento = evento + "END:VCALENDAR\n"
        qr = qrcode.QRCode(version=2, box_size=15, border=4)
        qr.add_data(evento)
        qr.make(fit=True)
        imagen = qr.make_image(fill_color="black", back_color="white")
        archivo = "qr_" + pedido.cliente.codigo + ".png"
        imagen.save(archivo)
        return archivo


class ComprobanteRotulado(Comprobante):
    def generar(self, pedido):
        entrega = pedido.entrega
        fecha = datetime.now().strftime("%Y-%m-%d")
        if entrega.modalidad == "recojo":
            titulo = "ROTULADO - ENTREGA EXTERNA (RECOJO)"
        else:
            titulo = "ROTULADO - ENTREGA EXTERNA (DELIVERY)"
        texto = "------------------------------------------------------\n"
        texto = texto + titulo + "\n"
        texto = texto + "------------------------------------------------------\n"
        texto = texto + "Sede origen: " + entrega.sede_origen + "\n"
        texto = texto + "Entregado por: " + entrega.remitente + "\n"
        texto = texto + "Destinatario: " + entrega.destinatario + "\n"
        if entrega.modalidad == "delivery":
            texto = texto + "Direccion: " + entrega.direccion + "\n"
        texto = texto + "Sede destino: " + entrega.sede_destino + "\n"
        texto = texto + "Prendas: " + pedido.prendas + " | Cantidad: " + str(pedido.cantidad) + "\n"
        texto = texto + "Peso: " + str(pedido.peso) + " kg\n"
        texto = texto + "Fecha: " + fecha + "\n"
        texto = texto + "------------------------------------------------------"
        imagen = PILImage.new("RGB", (600, 420), color="white")
        dibujo = ImageDraw.Draw(imagen)
        fuente = cargar_fuente()
        dibujo.multiline_text((20, 20), texto, fill="black", font=fuente, spacing=6)
        archivo = "rotulado_" + pedido.cliente.codigo + ".png"
        imagen.save(archivo)
        return archivo


class Entrega(ABC):
    def __init__(self, peso):
        self.peso = peso

    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    @abstractmethod
    def crear_comprobante(self):
        pass

    def calcular_total(self):
        costo = self.calcular_costo()
        igv = costo * 0.18
        return costo + igv

    def generar_comprobante(self, pedido):
        comprobante = self.crear_comprobante()
        return comprobante.generar(pedido)


class EntregaInterna(Entrega):
    def __init__(self, peso, motorizado, placa, fecha_hora):
        super().__init__(peso)
        self.motorizado = motorizado
        self.placa = placa
        self.fecha_hora = fecha_hora

    def calcular_costo(self):
        return 8 + 2 * self.peso

    def descripcion(self):
        return "Entrega Interna (QR)"

    def crear_comprobante(self):
        return ComprobanteQR()


class EntregaExterna(Entrega):
    def __init__(self, peso, modalidad, sede_origen, sede_destino, remitente, destinatario, direccion):
        super().__init__(peso)
        self.modalidad = modalidad
        self.sede_origen = sede_origen
        self.sede_destino = sede_destino
        self.remitente = remitente
        self.destinatario = destinatario
        self.direccion = direccion

    def calcular_costo(self):
        if self.modalidad == "recojo":
            return 5 + 1 * self.peso
        else:
            return 12 + 3.5 * self.peso

    def descripcion(self):
        return "Entrega Externa"

    def crear_comprobante(self):
        return ComprobanteRotulado()


class Pedido:
    def __init__(self, cliente, prendas, cantidad, peso):
        self.cliente = cliente
        self.prendas = prendas
        self.cantidad = cantidad
        self.peso = peso
        self.entrega = None


class GestorPedidos:
    def __init__(self):
        self.pedidos = []

    def agregar(self, pedido):
        self.pedidos.append(pedido)

    def existe(self, codigo):
        for pedido in self.pedidos:
            if pedido.cliente.codigo == codigo:
                return True
        return False

    def buscar(self, codigo):
        for pedido in self.pedidos:
            if pedido.cliente.codigo == codigo:
                return pedido
        raise PedidoNoEncontradoError("No existe un pedido con el codigo " + codigo + ".")

    def listar(self):
        return self.pedidos

    def exportar_excel(self):
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Pedidos"
        hoja.append([
            "Codigo Cliente", "Nombre", "Prendas", "Cantidad", "Peso (kg)",
            "Codigo de Barras", "Entrega", "QR / Rotulado", "Costo Envio (S/)", "Total con IGV (S/)"
        ])
        temporales = []
        fila = 1
        for pedido in self.pedidos:
            fila = fila + 1
            if pedido.entrega is None:
                estado = "Pendiente"
                costo = 0
                total = 0
            else:
                estado = pedido.entrega.descripcion()
                costo = pedido.entrega.calcular_costo()
                total = pedido.entrega.calcular_total()
            hoja.append([
                pedido.cliente.codigo, pedido.cliente.nombre, pedido.prendas, pedido.cantidad,
                pedido.peso, "", estado, "", round(costo, 2), round(total, 2)
            ])
            archivo_barras = crear_codigo_barras(pedido.cliente.codigo)
            temporales.append(archivo_barras)
            imagen_barras = Image(archivo_barras)
            imagen_barras.width = 150
            imagen_barras.height = 50
            hoja.add_image(imagen_barras, "F" + str(fila))
            if pedido.entrega is not None:
                archivo = pedido.entrega.generar_comprobante(pedido)
                temporales.append(archivo)
                imagen = Image(archivo)
                if isinstance(pedido.entrega, EntregaInterna):
                    imagen.width = 150
                    imagen.height = 150
                else:
                    imagen.width = 250
                    imagen.height = 250
                hoja.add_image(imagen, "H" + str(fila))
        libro.save("pedido_registrado.xlsx")
        for archivo in temporales:
            if os.path.exists(archivo):
                os.remove(archivo)
        print("Excel generado: pedido_registrado.xlsx")


def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        try:
            if texto == "":
                raise DatoInvalidoError("El dato no puede estar vacio.")
            return texto
        except DatoInvalidoError as error:
            print("Error: " + str(error))


def pedir_entero(mensaje):
    while True:
        try:
            numero = int(input(mensaje))
            if numero <= 0:
                raise DatoInvalidoError("El numero debe ser mayor que cero.")
            return numero
        except ValueError:
            print("Error: debe ingresar un numero entero.")
        except DatoInvalidoError as error:
            print("Error: " + str(error))


def pedir_decimal(mensaje):
    while True:
        try:
            numero = float(input(mensaje))
            if numero <= 0:
                raise DatoInvalidoError("El numero debe ser mayor que cero.")
            return numero
        except ValueError:
            print("Error: debe ingresar un numero.")
        except DatoInvalidoError as error:
            print("Error: " + str(error))


def pedir_fecha(mensaje):
    while True:
        fecha = input(mensaje).strip()
        try:
            datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            return fecha
        except ValueError:
            print("Error: use el formato YYYY-MM-DD HH:MM.")


def registrar_pedido(gestor):
    print("\n=== REGISTRO DE PEDIDO ===")
    codigo = pedir_texto("Codigo del cliente: ")
    if gestor.existe(codigo):
        print("Ya existe un pedido con ese codigo.")
        return
    nombre = pedir_texto("Nombre del cliente: ")
    prendas = pedir_texto("Tipo de prendas: ")
    cantidad = pedir_entero("Cantidad de prendas: ")
    peso = pedir_decimal("Peso del paquete (kg): ")
    cliente = Cliente(codigo, nombre)
    pedido = Pedido(cliente, prendas, cantidad, peso)
    gestor.agregar(pedido)
    print("Pedido registrado correctamente.")


def procesar_entrega(gestor):
    print("\n=== ENTREGA ===")
    codigo = pedir_texto("Codigo del cliente: ")
    try:
        pedido = gestor.buscar(codigo)
    except PedidoNoEncontradoError as error:
        print("Error: " + str(error))
        return
    if pedido.entrega is not None:
        print("Este pedido ya tiene una entrega.")
        return
    tipo = input("Tipo de entrega (interna / externa): ").strip().lower()
    if tipo == "interna":
        motorizado = pedir_texto("Nombre del motorizado: ")
        placa = pedir_texto("Numero de placa: ")
        fecha = pedir_fecha("Fecha y hora estimada (YYYY-MM-DD HH:MM): ")
        pedido.entrega = EntregaInterna(pedido.peso, motorizado, placa, fecha)
    elif tipo == "externa":
        print("1. Recojo en tienda")
        print("2. Delivery")
        opcion = input("Seleccione (1 o 2): ").strip()
        sede_origen = pedir_texto("Sede de origen: ")
        remitente = pedir_texto("Nombre de quien entrega: ")
        if opcion == "1":
            destinatario = pedir_texto("Nombre de quien recoge: ")
            sede_destino = pedir_texto("Sede destino: ")
            pedido.entrega = EntregaExterna(pedido.peso, "recojo", sede_origen, sede_destino, remitente, destinatario, "")
        else:
            destinatario = pedir_texto("Nombre de quien recibe: ")
            direccion = pedir_texto("Direccion completa: ")
            sede_destino = pedir_texto("Sede destino: ")
            pedido.entrega = EntregaExterna(pedido.peso, "delivery", sede_origen, sede_destino, remitente, destinatario, direccion)
    else:
        print("Tipo de entrega no valido.")
        return
    print("Entrega registrada: " + pedido.entrega.descripcion())
    print("Costo de envio: S/ " + str(round(pedido.entrega.calcular_costo(), 2)))
    print("Total con IGV: S/ " + str(round(pedido.entrega.calcular_total(), 2)))


def mostrar_pedido(gestor):
    print("\n=== BUSCAR PEDIDO ===")
    codigo = pedir_texto("Codigo del cliente: ")
    try:
        pedido = gestor.buscar(codigo)
    except PedidoNoEncontradoError as error:
        print("Error: " + str(error))
        return
    print("Cliente: " + pedido.cliente.codigo + " - " + pedido.cliente.nombre)
    print("Prendas: " + pedido.prendas + " | Cantidad: " + str(pedido.cantidad) + " | Peso: " + str(pedido.peso) + " kg")
    if pedido.entrega is None:
        print("Estado: Pendiente")
    else:
        print("Estado: " + pedido.entrega.descripcion())
        print("Costo de envio: S/ " + str(round(pedido.entrega.calcular_costo(), 2)))
        print("Total con IGV: S/ " + str(round(pedido.entrega.calcular_total(), 2)))


def listar_pedidos(gestor):
    print("\n=== LISTA DE PEDIDOS ===")
    lista = gestor.listar()
    if len(lista) == 0:
        print("No hay pedidos registrados.")
        return
    numero = 1
    for pedido in lista:
        if pedido.entrega is None:
            estado = "Pendiente"
            total = 0
        else:
            estado = pedido.entrega.descripcion()
            total = pedido.entrega.calcular_total()
        print(str(numero) + ". " + pedido.cliente.codigo + " - " + pedido.cliente.nombre + " | " + estado + " | Total: S/ " + str(round(total, 2)))
        numero = numero + 1


def calcular_costo(gestor):
    print("\n=== CALCULO DE COSTO DE ENVIO ===")
    codigo = pedir_texto("Codigo del cliente: ")
    try:
        pedido = gestor.buscar(codigo)
    except PedidoNoEncontradoError as error:
        print("Error: " + str(error))
        return
    if pedido.entrega is None:
        print("El pedido todavia no tiene una entrega.")
        return
    costo = pedido.entrega.calcular_costo()
    igv = costo * 0.18
    total = costo + igv
    print("Tipo de entrega: " + pedido.entrega.descripcion())
    print("Subtotal: S/ " + str(round(costo, 2)))
    print("IGV (18%): S/ " + str(round(igv, 2)))
    print("Total a pagar: S/ " + str(round(total, 2)))


def menu():
    gestor = GestorPedidos()
    opcion = ""
    while opcion != "7":
        print("\n===== SISTEMA DE GESTION DE PEDIDOS - TENDENCIAS SHEIN PERU =====")
        print("1. Registrar pedido")
        print("2. Procesar entrega")
        print("3. Buscar pedido")
        print("4. Listar pedidos")
        print("5. Calcular costo de envio")
        print("6. Exportar reporte a Excel")
        print("7. Salir")
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "1":
            registrar_pedido(gestor)
        elif opcion == "2":
            procesar_entrega(gestor)
        elif opcion == "3":
            mostrar_pedido(gestor)
        elif opcion == "4":
            listar_pedidos(gestor)
        elif opcion == "5":
            calcular_costo(gestor)
        elif opcion == "6":
            if len(gestor.listar()) == 0:
                print("No hay pedidos para exportar.")
            else:
                gestor.exportar_excel()
        elif opcion == "7":
            print("Gracias por usar el sistema.")
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    menu()
