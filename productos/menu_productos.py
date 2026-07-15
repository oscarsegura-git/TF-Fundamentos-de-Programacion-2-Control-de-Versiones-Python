from comun import entrada
from comun.excepciones import (DatoInvalidoError, ProductoDuplicadoError,
                               ProductoNoEncontradoError)
from productos.producto import CATEGORIAS

class MenuProductos:
    def __init__(self, gestor_productos):
        self.__gestor = gestor_productos

    def mostrar(self):
        opcion = ""
        while opcion != "6":
            entrada.titulo("Gestión de Productos")
            print("  1. Registrar producto")
            print("  2. Buscar producto")
            print("  3. Listar catálogo")
            print("  4. Actualizar producto")
            print("  5. Desactivar / Activar producto")
            print("  6. Volver al menú principal")
            print(entrada.linea())
            opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4", "5", "6"])
            if opcion == "1":
                self._registrar()
            elif opcion == "2":
                self._buscar()
            elif opcion == "3":
                self._listar()
            elif opcion == "4":
                self._actualizar()
            elif opcion == "5":
                self._cambiar_estado()

    def _elegir_categoria(self):
        print(" Categoría   :")
        fila = "  "
        for i in range(len(CATEGORIAS)):
            fila += (" " + str(i + 1) + ". " + CATEGORIAS[i]).ljust(21)
            if (i + 1) % 3 == 0:
                print(fila)
                fila = "  "
        if fila.strip() != "":
            print(fila)
        opciones = [str(i + 1) for i in range(len(CATEGORIAS))]
        indice = int(entrada.pedir_opcion(" Opción: ", opciones))
        return CATEGORIAS[indice - 1]

    def _registrar(self):
        entrada.titulo("Registrar producto")
        codigo = entrada.pedir_texto(" Código      : ")
        nombre = entrada.pedir_texto(" Nombre      : ")
        print(entrada.linea())
        categoria = self._elegir_categoria()
        print(entrada.linea())
        precio = entrada.pedir_decimal(" Precio (S/): ")
        print(entrada.linea())
        try:
            self.__gestor.registrar(codigo, nombre, categoria, precio)
            print(" [OK] Producto registrado exitosamente.")
        except (ProductoDuplicadoError, DatoInvalidoError) as error:
            print(" [ERROR] " + str(error))
        entrada.pausar()

    def _buscar(self):
        entrada.titulo("Buscar producto")
        texto = entrada.pedir_texto(" Ingrese código o nombre: ")
        print(entrada.linea())
        try:
            encontrados = self.__gestor.buscar_por_texto(texto)
        except ProductoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        for producto in encontrados:
            print(" Producto encontrado:")
            print("  Código    : " + producto.codigo)
            print("  Nombre    : " + producto.nombre)
            print("  Categoría : " + producto.categoria)
            print("  Precio    : S/ " + format(producto.precio, ".2f"))
            print("  Estado    : " + producto.estado_texto())
            print(entrada.linea())
        entrada.pausar()

    def _fila(self, codigo, nombre, categoria, precio, estado):
        return ("  " + codigo.ljust(7) + nombre.ljust(30)[:30] +
                categoria.ljust(16)[:16] + precio.rjust(10) + "   " + estado)

    def _listar(self):
        entrada.titulo("Catálogo de productos")
        productos = self.__gestor.listar()
        if not productos:
            print(" [INFO] El catálogo está vacío.")
            entrada.pausar()
            return
        print(self._fila("CÓD", "NOMBRE", "CATEGORÍA", "PRECIO", "ESTADO"))
        print(entrada.linea())
        for producto in productos:
            print(self._fila(producto.codigo, producto.nombre, producto.categoria,
                             "S/ " + format(producto.precio, ".2f"),
                             producto.estado_texto()))
        print(entrada.linea())
        activos = self.__gestor.cantidad_activos()
        print(" Total activos: " + str(activos) +
              "  |  Total inactivos: " + str(len(productos) - activos))
        entrada.pausar()

    def _actualizar(self):
        entrada.titulo("Actualizar producto")
        codigo = entrada.pedir_texto(" Código del producto: ")
        try:
            producto = self.__gestor.buscar(codigo)
        except ProductoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        print(" Producto: " + producto.nombre)
        print(entrada.linea())
        print(" ¿Qué desea actualizar?  (el código no se puede modificar)")
        print("  1. Nombre")
        print("  2. Categoría")
        print("  3. Precio")
        print("  4. Cancelar")
        opcion = entrada.pedir_opcion(" Opción: ", ["1", "2", "3", "4"])
        if opcion == "4":
            print(" [INFO] Actualización cancelada.")
            entrada.pausar()
            return
        print(entrada.linea())
        if opcion == "1":
            producto.nombre = entrada.pedir_texto(" Nuevo nombre: ")
        elif opcion == "2":
            producto.categoria = self._elegir_categoria()
        else:
            print(" Precio actual: S/ " + format(producto.precio, ".2f"))
            producto.precio = entrada.pedir_decimal(" Nuevo precio (S/): ")
        print(entrada.linea())
        print(" [OK] Producto actualizado exitosamente.")
        entrada.pausar()

    def _cambiar_estado(self):
        entrada.titulo("Desactivar / Activar producto")
        codigo = entrada.pedir_texto(" Código del producto: ")
        try:
            producto = self.__gestor.buscar(codigo)
        except ProductoNoEncontradoError as error:
            print(" [ERROR] " + str(error))
            entrada.pausar()
            return
        print(entrada.linea())
        if producto.activo:
            producto.desactivar()
            print(" [OK] Producto DESACTIVADO. Ya no aparece al registrar pedidos,")
            print("      pero su historial se conserva.")
        else:
            producto.activar()
            print(" [OK] Producto ACTIVADO nuevamente.")
        entrada.pausar()
