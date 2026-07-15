from datetime import date, timedelta

from comun import entrada
from comun.excepciones import EntregaNoDisponibleError, PedidoNoEncontradoError
from pedidos.pedido import ESTADOS

class MenuReportes:
    def __init__(self, gestor_reportes, gestor_pedidos):
        self.__gestor = gestor_reportes
        self.__gestor_pedidos = gestor_pedidos

    def mostrar(self):
        opcion = ""
        while opcion != "5":
            entrada.titulo("Reportes")
            print("  1. Consultar pedidos por estado")
            print("  2. Consultar pedidos por cliente")
            print("  3. Calcular costo de envío")
            print("  4. Exportar reporte a Excel")
            print("  5. Volver al menú principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4", "5"])
            if opcion == "1":
                self._por_estado()
            elif opcion == "2":
                self._por_cliente()
            elif opcion == "3":
                self._costo_envio()
            elif opcion == "4":
                self._exportar()

    def _fila(self, codigo, cliente, peso, actualizacion):
        return ("  " + codigo.ljust(20) + cliente.ljust(22)[:22] +
                peso.ljust(9) + actualizacion)

    def _tabla(self, pedidos, etiqueta_total):
        if not pedidos:
            print(" [INFO] No hay pedidos para el filtro seleccionado.")
            entrada.pausar()
            return
        print(entrada.linea())
        print(self._fila("CÓDIGO", "CLIENTE", "PESO", "ÚLTIMA ACTUALIZACIÓN"))
        print(entrada.linea())
        for pedido in pedidos:
            print(self._fila(pedido.codigo, pedido.cliente.nombre,
                             str(pedido.peso) + "kg", pedido.ultima_actualizacion()))
        print(entrada.linea())
        print(" " + etiqueta_total + ": " + str(len(pedidos)))
        entrada.pausar()

    def _por_estado(self):
        entrada.titulo("Pedidos por estado")
        print(" Seleccione estado:")
        for i in range(len(ESTADOS)):
            print("   " + str(i + 1) + ". " + ESTADOS[i])
        opciones = [str(i + 1) for i in range(len(ESTADOS))]
        indice = int(entrada.pedir_opcion(" Opción: ", opciones))
        estado = ESTADOS[indice - 1]
        self._tabla(self.__gestor.filtrar(estado=estado), "Total en " + estado.lower())

    def _por_cliente(self):
        entrada.titulo("Pedidos por cliente")
        dni = entrada.pedir_texto(" DNI del cliente: ")
        self._tabla(self.__gestor.filtrar(dni=dni), "Total de pedidos del cliente")

    def _costo_envio(self):
        entrada.titulo("Calcular costo de envío")
        codigo = entrada.pedir_texto(" Código de pedido : ")
        try:
            pedido = self.__gestor_pedidos.buscar_por_codigo(codigo)
        except PedidoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        try:
            subtotal, igv, total = self.__gestor.costo_envio(pedido)
        except EntregaNoDisponibleError as error:
            print(entrada.linea())
            print(" [ERROR] No es posible calcular el costo.")
            print(" " + str(error))
            entrada.pausar()
            return
        entrega = pedido.entrega
        print(" [OK] " + entrega.nombre_tipo() + " asignada. Peso: " +
              str(pedido.peso) + " kg")
        print(entrada.linea())
        print(" Tarifa base       : S/ " + format(entrega.tarifa_base(), "5.2f"))
        print(" Tarifa por kg     : S/ " + format(entrega.tarifa_por_kg(), "5.2f"))
        print(entrada.linea())
        print(" Subtotal          : S/ " + format(subtotal, "5.2f"))
        print(" IGV (18%)         : S/ " + format(igv, "5.2f"))
        print(entrada.linea())
        print(" TOTAL A PAGAR     : S/ " + format(total, "5.2f"))
        entrada.pausar()

    def _exportar(self):
        entrada.titulo("Exportar reporte")
        print(" Exportar:")
        print("   1. Pedidos de hoy")
        print("   2. Esta semana")
        print("   3. Rango de fechas personalizado")
        opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3"])
        hoy = date.today()
        if opcion == "1":
            desde = hoy
            hasta = hoy
            etiqueta = "Total del día"
        elif opcion == "2":
            desde = hoy - timedelta(days=hoy.weekday())
            hasta = hoy
            etiqueta = "Total de la semana"
        else:
            desde = entrada.pedir_dia(" Desde (AAAA-MM-DD): ")
            hasta = entrada.pedir_dia(" Hasta (AAAA-MM-DD): ")
            etiqueta = "Total del período"
        print(entrada.linea())
        pedidos = self.__gestor.filtrar(desde=desde, hasta=hasta)
        if not pedidos:
            print(" [INFO] No hay pedidos en el período seleccionado.")
            entrada.pausar()
            return
        if desde == hasta:
            print(" Generando reporte del " + desde.strftime("%d/%m/%Y") + "...")
            nombre = "reporte_" + desde.strftime("%d%m%Y")
        else:
            print(" Generando reporte del " + desde.strftime("%d/%m/%Y") +
                  " al " + hasta.strftime("%d/%m/%Y") + "...")
            nombre = "reporte_" + desde.strftime("%d%m%Y") + "_" + hasta.strftime("%d%m%Y")
        ruta = self.__gestor.exportar_excel(pedidos, nombre)
        print(" [OK] Archivo generado: " + ruta)
        print(" Pedidos incluidos : " + str(len(pedidos)))
        print(" " + etiqueta.ljust(17) + " : S/ " +
              format(self.__gestor.total_periodo(pedidos), ",.2f"))
        print(entrada.linea())
        entrada.pausar()
