from comun import entrada
from comun.excepciones import (ClienteDuplicadoError, ClienteNoEncontradoError,
                               DatoInvalidoError, DniInvalidoError)

class MenuClientes:
    def __init__(self, gestor_clientes, gestor_pedidos):
        self.__gestor = gestor_clientes
        self.__gestor_pedidos = gestor_pedidos

    def mostrar(self):
        opcion = ""
        while opcion != "5":
            entrada.titulo("Gestión de Clientes")
            print("  1. Registrar cliente")
            print("  2. Buscar cliente")
            print("  3. Listar clientes")
            print("  4. Actualizar cliente")
            print("  5. Volver al menú principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4", "5"])
            if opcion == "1":
                self._registrar()
            elif opcion == "2":
                self._buscar()
            elif opcion == "3":
                self._listar()
            elif opcion == "4":
                self._actualizar()

    def _contar_pedidos(self, dni):
        return len(self.__gestor_pedidos.pedidos_de_cliente(dni))

    def _pedir_dni(self):
        while True:
            dni = entrada.pedir_texto(" DNI             : ")
            try:
                if not (len(dni) == 8 and dni.isdigit()):
                    raise DniInvalidoError(
                        "El DNI debe contener exactamente 8 dígitos numéricos.")
                return dni
            except DniInvalidoError as error:
                print(" [ERROR] " + str(error))
                print(" Ingrese nuevamente:")

    def _registrar(self):
        entrada.titulo("Registrar cliente")
        nombre = entrada.pedir_texto(" Nombre completo : ")
        dni = self._pedir_dni()
        telefono = entrada.pedir_texto(" Teléfono        : ")
        direccion = entrada.pedir_texto(" Dirección       : ")
        distrito = entrada.pedir_texto(" Distrito        : ")
        ciudad = entrada.pedir_texto(" Ciudad          : ")
        print(entrada.linea())
        try:
            self.__gestor.registrar(dni, nombre, telefono, direccion, ciudad, distrito)
            print(" [OK] Cliente registrado exitosamente.")
        except (ClienteDuplicadoError, DatoInvalidoError) as error:
            print(" [ERROR] " + str(error))
        entrada.pausar()

    def _buscar(self):
        entrada.titulo("Buscar cliente")
        texto = entrada.pedir_texto(" Ingrese DNI o nombre: ")
        print(entrada.linea())
        try:
            encontrados = self.__gestor.buscar_por_texto(texto)
        except ClienteNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        for cliente in encontrados:
            print(" Cliente encontrado:")
            print("  Nombre    : " + cliente.nombre)
            print("  DNI       : " + cliente.dni)
            print("  Teléfono  : " + cliente.telefono)
            print("  Dirección : " + cliente.direccion_completa())
            print("  Pedidos   : " + str(self._contar_pedidos(cliente.dni)) +
                  " pedidos registrados")
            print(entrada.linea())
        entrada.pausar()

    def _fila(self, dni, nombre, telefono, pedidos):
        return ("  " + dni.ljust(11) + nombre.ljust(30)[:30] +
                telefono.ljust(14) + pedidos)

    def _listar(self):
        entrada.titulo("Listado de clientes")
        clientes = self.__gestor.listar()
        if not clientes:
            print(" [INFO] No hay clientes registrados.")
            entrada.pausar()
            return
        print(self._fila("DNI", "NOMBRE", "TELÉFONO", "PEDIDOS"))
        print(entrada.linea())
        for cliente in clientes:
            print(self._fila(cliente.dni, cliente.nombre, cliente.telefono,
                             str(self._contar_pedidos(cliente.dni))))
        print(entrada.linea())
        print(" Total de clientes registrados: " + str(self.__gestor.cantidad()))
        entrada.pausar()

    def _actualizar(self):
        entrada.titulo("Actualizar cliente")
        dni = entrada.pedir_texto(" Ingrese DNI del cliente: ")
        try:
            cliente = self.__gestor.buscar(dni)
        except ClienteNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        print(" Cliente: " + cliente.nombre)
        print(entrada.linea())
        print(" ¿Qué desea actualizar?  (el DNI no se puede modificar)")
        print("  1. Nombre")
        print("  2. Teléfono")
        print("  3. Dirección")
        print("  4. Cancelar")
        opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4"])
        if opcion == "4":
            print(" [INFO] Actualización cancelada.")
            entrada.pausar()
            return
        print(entrada.linea())
        if opcion == "1":
            cliente.nombre = entrada.pedir_texto(" Nuevo nombre: ")
        elif opcion == "2":
            cliente.telefono = entrada.pedir_texto(" Nuevo teléfono: ")
        else:
            cliente.direccion = entrada.pedir_texto(" Nueva dirección: ")
            cliente.distrito = entrada.pedir_texto(" Nuevo distrito : ")
            cliente.ciudad = entrada.pedir_texto(" Nueva ciudad   : ")
        print(entrada.linea())
        print(" [OK] Datos actualizados exitosamente.")
        entrada.pausar()

