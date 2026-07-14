from comun import entrada
from comun.excepciones import (ClienteDuplicadoError, ClienteNoEncontradoError,
                               DniInvalidoError)

class MenuClientes:
    def __init__(self, gestor_clientes, gestor_pedidos):
        self.gestor = gestor_clientes
        self.gestor_pedidos = gestor_pedidos

    def mostrar(self):
        opcion = ""
        while opcion != "5":
            print("\n" + entrada.linea())
            print(" MODULO 1 - GESTION DE CLIENTES")
            print(entrada.linea())
            print("  1. Registrar cliente")
            print("  2. Buscar cliente")
            print("  3. Listar clientes")
            print("  4. Actualizar cliente")
            print("  5. Volver al menu principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opcion: ", ["1", "2", "3", "4", "5"])
            if opcion == "1":
                self._registrar()
            elif opcion == "2":
                self._buscar()
            elif opcion == "3":
                self._listar()
            elif opcion == "4":
                self._actualizar()

    def _pedir_dni(self):
        while True:
            dni = entrada.pedir_texto(" DNI (8 digitos): ")
            try:
                if not (len(dni) == 8 and dni.isdigit()):
                    raise DniInvalidoError(
                        "El DNI debe tener exactamente 8 digitos numericos.")
                return dni
            except DniInvalidoError as error:
                print("  [ERROR] " + str(error))

    def _registrar(self):
        print("\n --- Registrar cliente ---")
        dni = self._pedir_dni()
        nombre = entrada.pedir_texto(" Nombre completo : ")
        telefono = entrada.pedir_texto(" Telefono        : ")
        direccion = entrada.pedir_texto(" Direccion       : ")
        ciudad = entrada.pedir_texto(" Ciudad          : ")
        distrito = entrada.pedir_texto(" Distrito        : ")
        try:
            self.gestor.registrar(dni, nombre, telefono, direccion, ciudad, distrito)
            print(" [OK] Cliente registrado exitosamente.")
        except ClienteDuplicadoError as error:
            print(" [ERROR] " + str(error))

    def _buscar(self):
        print("\n --- Buscar cliente ---")
        dni = entrada.pedir_texto(" DNI a buscar: ")
        try:
            cliente = self.gestor.buscar(dni)
            print(entrada.linea())
            print("  Nombre    : " + cliente.nombre)
            print("  DNI       : " + cliente.dni)
            print("  Telefono  : " + cliente.telefono)
            print("  Direccion : " + cliente.direccion +
                  " (" + cliente.distrito + ", " + cliente.ciudad + ")")
            print("  Pedidos   : " + str(self._contar_pedidos(cliente.dni)))
        except ClienteNoEncontradoError as error:
            print(" [ERROR] " + str(error))

    def _contar_pedidos(self, dni):
        return len(self.gestor_pedidos.pedidos_de_cliente(dni))

    def _listar(self):
        print("\n --- Listar clientes ---")
        clientes = self.gestor.listar()
        if not clientes:
            print(" No hay clientes registrados.")
            return
        print(entrada.linea())
        print("  DNI        NOMBRE                    TELEFONO      PEDIDOS")
        print(entrada.linea())
        for c in clientes:
            print("  " + c.dni.ljust(9) + "  " + c.nombre.ljust(24)[:24] +
                  "  " + c.telefono.ljust(11) + "   " + str(self._contar_pedidos(c.dni)))
        print(entrada.linea())
        print(" Total de clientes registrados: " + str(self.gestor.cantidad()))

    def _actualizar(self):
        print("\n --- Actualizar cliente (el DNI no se puede modificar) ---")
        dni = entrada.pedir_texto(" DNI del cliente: ")
        try:
            cliente = self.gestor.buscar(dni)
        except ClienteNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            return
        print(" Deje el campo vacio para conservar el valor actual.")
        nombre = input(" Nombre [" + cliente.nombre + "]: ").strip()
        telefono = input(" Telefono [" + cliente.telefono + "]: ").strip()
        direccion = input(" Direccion [" + cliente.direccion + "]: ").strip()
        ciudad = input(" Ciudad [" + cliente.ciudad + "]: ").strip()
        distrito = input(" Distrito [" + cliente.distrito + "]: ").strip()
        self.gestor.actualizar(dni,
                               nombre or None, telefono or None,
                               direccion or None, ciudad or None, distrito or None)
        print(" [OK] Datos actualizados (DNI intacto: " + cliente.dni + ").")
