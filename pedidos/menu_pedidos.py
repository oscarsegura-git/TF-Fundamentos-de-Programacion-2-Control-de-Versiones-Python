from comun import entrada, recursos
from comun.excepciones import (ClienteNoEncontradoError, DatoInvalidoError,
                               PedidoNoEncontradoError, TransicionInvalidaError)
from pedidos.pedido import COMPRADO, EN_CAMINO, LISTO_RECOJO, MEDIOS_PAGO

class MenuPedidos:
    def __init__(self, gestor_pedidos, gestor_clientes, gestor_productos):
        self.__gestor = gestor_pedidos
        self.__gestor_clientes = gestor_clientes
        self.__gestor_productos = gestor_productos

    def mostrar(self):
        opcion = ""
        while opcion != "4":
            entrada.titulo("Gestión de Pedidos")
            print("  1. Registrar pedido")
            print("  2. Buscar pedido")
            print("  3. Actualizar estado")
            print("  4. Volver al menú principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4"])
            if opcion == "1":
                self._registrar()
            elif opcion == "2":
                self._buscar()
            elif opcion == "3":
                self._actualizar_estado()

    def _registrar(self):
        entrada.titulo("Registrar pedido")
        dni = entrada.pedir_texto(" DNI del cliente   : ")
        try:
            cliente = self.__gestor_clientes.buscar(dni)
        except ClienteNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            print("         Regístrelo primero en el Módulo de Clientes.")
            entrada.pausar()
            return
        print(" [OK] Cliente: " + cliente.nombre)
        print(entrada.linea())
        tipo_prenda = entrada.pedir_texto(" Tipo de prenda    : ")
        cantidad = entrada.pedir_entero(" Cantidad          : ", minimo=1)
        peso = entrada.pedir_decimal(" Peso (kg)         : ")
        pedido = self.__gestor.registrar(dni, tipo_prenda, cantidad, peso)
        self._agregar_productos(pedido)
        ruta_barras = recursos.generar_codigo_barras(pedido.codigo)
        print(entrada.linea())
        print(" Código generado   : " + pedido.codigo)
        print(" Código de barras  : " + ruta_barras)
        print(" Estado            : " + pedido.estado)
        print(entrada.linea())
        print(" [OK] Pedido registrado exitosamente.")
        entrada.pausar()

    def _agregar_productos(self, pedido):
        disponibles = self.__gestor_productos.listar_disponibles()
        if not disponibles:
            return
        print(entrada.linea())
        agregar = input(" ¿Desea asociar productos del catálogo? (s/n): ").strip().lower()
        if agregar != "s":
            return
        while True:
            print(" Productos disponibles:")
            for producto in disponibles:
                print("   " + str(producto))
            codigo = input(" Código de producto (Enter para terminar): ").strip()
            if codigo == "":
                return
            try:
                producto = self.__gestor_productos.buscar(codigo)
            except Exception as error:
                print("  [ERROR] " + str(error))
                continue
            if not producto.activo:
                print("  [ERROR] Producto inactivo, no disponible.")
                continue
            cantidad = entrada.pedir_entero("   Cantidad: ", minimo=1)
            pedido.agregar_linea(producto, cantidad)
            print("   [OK] Agregado. Subtotal productos: S/ " +
                  format(pedido.total_productos(), ".2f"))

    def _buscar(self):
        entrada.titulo("Buscar pedido")
        texto = entrada.pedir_texto(" Ingrese código, DNI o nombre: ")
        print(entrada.linea())
        try:
            encontrados = self.__gestor.buscar(texto)
        except PedidoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        for pedido in encontrados:
            print(" Pedido encontrado:")
            print("  Código      : " + pedido.codigo)
            print("  Cliente     : " + pedido.cliente.nombre +
                  " (DNI " + pedido.cliente.dni + ")")
            print("  Prenda      : " + pedido.tipo_prenda +
                  "  |  Cantidad: " + str(pedido.cantidad) +
                  "  |  Peso: " + str(pedido.peso) + " kg")
            print("  Estado      : " + pedido.estado)
            print("  Actualizado : " + pedido.ultima_actualizacion())
            if pedido.metodo_pago is not None:
                print("  Pago        : " + pedido.metodo_pago + " — S/ " +
                      format(pedido.monto_pagado, ".2f") +
                      " (" + pedido.fecha_pago + ")")
            if pedido.entrega is not None:
                print("  Entrega     : " + pedido.entrega.descripcion())
            print(entrada.linea())
        entrada.pausar()

    def _actualizar_estado(self):
        entrada.titulo("Actualizar estado")
        codigo = entrada.pedir_texto(" Código de pedido : ")
        try:
            pedido = self.__gestor.buscar_por_codigo(codigo)
        except PedidoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        print(" Estado actual    : " + pedido.estado)
        print(entrada.linea())
        siguientes = [estado for estado in pedido.estados_siguientes()
                     if estado not in (EN_CAMINO, LISTO_RECOJO)]
        if not siguientes:
            print(" [INFO] El pedido está en un estado final, o su siguiente paso")
            print("        depende de asignar una entrega (Módulo de Entregas).")
            entrada.pausar()
            return
        print(" Seleccione nuevo estado:")
        for i in range(len(siguientes)):
            etiqueta = siguientes[i]
            if etiqueta == COMPRADO:
                etiqueta = "Pagar pedido (marca como \"" + COMPRADO + "\")"
            print("   " + str(i + 1) + ". " + etiqueta)
        opciones = [str(i + 1) for i in range(len(siguientes))]
        indice = int(entrada.pedir_opcion(" Opción: ", opciones))
        nuevo = siguientes[indice - 1]
        print(entrada.linea())
        if nuevo == COMPRADO:
            self._pagar(pedido)
            return
        try:
            pedido.cambiar_estado(nuevo)
            print(" [OK] Estado actualizado a: \"" + nuevo + "\" — " +
                  pedido.ultima_actualizacion())
        except TransicionInvalidaError as error:
            print(" [ERROR] " + str(error))
        entrada.pausar()

    def _pagar(self, pedido):
        entrada.titulo("Pagar pedido")
        total = pedido.total_productos()
        print(" Pedido            : " + pedido.codigo)
        print(" Cliente           : " + pedido.cliente.nombre)
        print(" Total productos   : S/ " + format(total, ".2f"))
        print(entrada.linea())
        print(" Medio de pago:")
        for i in range(len(MEDIOS_PAGO)):
            print("   " + str(i + 1) + ". " + MEDIOS_PAGO[i])
        opciones = [str(i + 1) for i in range(len(MEDIOS_PAGO))]
        indice = int(entrada.pedir_opcion(" Opción: ", opciones))
        metodo = MEDIOS_PAGO[indice - 1]
        if total > 0:
            monto = total
        else:
            monto = entrada.pedir_decimal(" Monto a pagar (S/): ", minimo=0.0,
                                          estricto=False)
        print(entrada.linea())
        try:
            pedido.registrar_pago(metodo, monto)
            print(" [OK] Pago registrado: " + metodo + " — S/ " +
                  format(monto, ".2f"))
            print(" [OK] Estado actualizado a: \"" + pedido.estado + "\" — " +
                  pedido.ultima_actualizacion())
        except (DatoInvalidoError, TransicionInvalidaError) as error:
            print(" [ERROR] " + str(error))
        entrada.pausar()
