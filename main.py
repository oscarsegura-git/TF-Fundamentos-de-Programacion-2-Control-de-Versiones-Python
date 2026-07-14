import datos_demo
from comun import entrada, recursos

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
        self.gestor_clientes = GestorClientes()
        self.gestor_productos = GestorProductos()
        self.gestor_pedidos = GestorPedidos(self.gestor_clientes)
        self.gestor_entregas = GestorEntregas(self.gestor_pedidos)
        self.gestor_reportes = GestorReportes(self.gestor_pedidos)

        self.menu_clientes = MenuClientes(self.gestor_clientes, self.gestor_pedidos)
        self.menu_productos = MenuProductos(self.gestor_productos)
        self.menu_pedidos = MenuPedidos(self.gestor_pedidos, self.gestor_clientes,
                                        self.gestor_productos)
        self.menu_entregas = MenuEntregas(self.gestor_entregas, self.gestor_pedidos)
        self.menu_reportes = MenuReportes(self.gestor_reportes, self.gestor_pedidos)

    def cargar_datos_demo(self):
        datos_demo.cargar(self.gestor_clientes, self.gestor_productos,
                          self.gestor_pedidos)

    def ejecutar(self):
        print("\n" + "=" * 54)
        print("SISTEMA DE GESTION DE PEDIDOS (SGP)")
        print("Tendencias Shein Peru")
        print("=" * 54)
        print(" Librerias de generacion de recursos:")
        print(recursos.estado_librerias())

        opcion = ""
        while opcion != "6":
            print("\n" + "=" * 54)
            print("   MENU PRINCIPAL")
            print("=" * 54)
            print("  1. Modulo de Clientes")
            print("  2. Modulo de Productos")
            print("  3. Modulo de Pedidos")
            print("  4. Modulo de Entregas")
            print("  5. Modulo de Reportes")
            print("  6. Salir")
            print("=" * 54)
            opcion = entrada.pedir_opcion(" Seleccione un modulo: ",
                                          ["1", "2", "3", "4", "5", "6"])
            if opcion == "1":
                self.menu_clientes.mostrar()
            elif opcion == "2":
                self.menu_productos.mostrar()
            elif opcion == "3":
                self.menu_pedidos.mostrar()
            elif opcion == "4":
                self.menu_entregas.mostrar()
            elif opcion == "5":
                self.menu_reportes.mostrar()
            elif opcion == "6":
                print("\n Gracias por usar el sistema. Hasta pronto.")

def main():
    sistema = SistemaGestionPedidos()
    sistema.cargar_datos_demo()
    sistema.ejecutar()

if __name__ == "__main__":
    main()
