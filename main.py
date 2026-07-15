import datos_demo
from comun import entrada, recursos, persistencia

from clientes.gestor_clientes import GestorClientes
from clientes.menu_clientes import MenuClientes
from productos.gestor_productos import GestorProductos
from productos.menu_productos import MenuProductos
from pedidos.gestor_pedidos import GestorPedidos
from pedidos.menu_pedidos import MenuPedidos
from entregas.gestor_entregas import GestorEntregas
from entregas.menu_entregas import MenuEntregas
from reportes.gestor_reportes import GestorReportes
from reportes.menu_reportes import MenuReportes

class SistemaGestionPedidos:
    def __init__(self):
        self.__gestor_clientes = GestorClientes()
        self.__gestor_productos = GestorProductos()
        self.__gestor_pedidos = GestorPedidos(self.__gestor_clientes)
        self.__gestor_entregas = GestorEntregas(self.__gestor_pedidos)
        self.__gestor_reportes = GestorReportes(self.__gestor_pedidos)

        self.__menu_clientes = MenuClientes(self.__gestor_clientes, self.__gestor_pedidos)
        self.__menu_productos = MenuProductos(self.__gestor_productos)
        self.__menu_pedidos = MenuPedidos(self.__gestor_pedidos, self.__gestor_clientes,
                                         self.__gestor_productos)
        self.__menu_entregas = MenuEntregas(self.__gestor_entregas)
        self.__menu_reportes = MenuReportes(self.__gestor_reportes, self.__gestor_pedidos)

    def cargar_datos_demo(self):
        datos_demo.cargar(self.__gestor_clientes, self.__gestor_productos,
                          self.__gestor_pedidos)

    def cargar_datos(self):
        if persistencia.existen_datos():
            if persistencia.cargar(self.__gestor_clientes, self.__gestor_productos,
                                   self.__gestor_pedidos):
                print("\n [INFO] Datos cargados desde " + persistencia.RUTA_DATOS)
                return
        self.cargar_datos_demo()

    def guardar_datos(self):
        persistencia.guardar(self.__gestor_clientes, self.__gestor_productos,
                             self.__gestor_pedidos)

    def ejecutar(self):
        faltantes = recursos.librerias_faltantes()
        if faltantes:
            print("\n [INFO] Librerías no instaladas: " + faltantes)
            print("        El sistema funciona igual y genera archivos de texto.")
        opcion = ""
        while opcion != "6":
            entrada.titulo("Tendencias Shein Perú — Sistema de Pedidos")
            print("  1. Gestión de Clientes")
            print("  2. Gestión de Productos")
            print("  3. Gestión de Pedidos")
            print("  4. Gestión de Entregas")
            print("  5. Reportes")
            print("  6. Salir")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Seleccione una opción: ",
                                          ["1", "2", "3", "4", "5", "6"])
            if opcion == "1":
                self.__menu_clientes.mostrar()
            elif opcion == "2":
                self.__menu_productos.mostrar()
            elif opcion == "3":
                self.__menu_pedidos.mostrar()
            elif opcion == "4":
                self.__menu_entregas.mostrar()
            elif opcion == "5":
                self.__menu_reportes.mostrar()
            elif opcion == "6":
                print("\n Gracias por usar el sistema. Hasta pronto.")
            self.guardar_datos()

def main():
    sistema = SistemaGestionPedidos()
    sistema.cargar_datos()
    try:
        sistema.ejecutar()
    finally:
        sistema.guardar_datos()

if __name__ == "__main__":
    main()

