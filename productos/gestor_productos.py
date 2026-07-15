from productos.producto import Producto
from comun.excepciones import ProductoDuplicadoError, ProductoNoEncontradoError

class GestorProductos:
    def __init__(self):
        self.__productos = []

    def _indice(self, codigo):
        codigo = str(codigo).strip().upper()
        for i in range(len(self.__productos)):
            if self.__productos[i].codigo == codigo:
                return i
        return -1

    def existe(self, codigo):
        return self._indice(codigo) >= 0

    def registrar(self, codigo, nombre, categoria, precio):
        producto = Producto(codigo, nombre, categoria, precio)
        if self.existe(producto.codigo):
            raise ProductoDuplicadoError(
                "Ya existe un producto con el código " + producto.codigo + ".")
        self.__productos.append(producto)
        return producto

    def buscar(self, codigo):
        indice = self._indice(codigo)
        if indice < 0:
            raise ProductoNoEncontradoError(
                "No existe un producto con el código " +
                str(codigo).strip().upper() + ".")
        return self.__productos[indice]

    def buscar_por_texto(self, texto):
        encontrados = [p for p in self.__productos if p.coincide(texto)]
        if not encontrados:
            raise ProductoNoEncontradoError(
                "No se encontraron productos para '" + str(texto).strip() + "'.")
        return encontrados

    def desactivar(self, codigo):
        producto = self.buscar(codigo)
        producto.desactivar()
        return producto

    def activar(self, codigo):
        producto = self.buscar(codigo)
        producto.activar()
        return producto

    def listar(self):
        return list(self.__productos)

    def listar_disponibles(self):
        return [p for p in self.__productos if p.activo]

    def cantidad_activos(self):
        return len(self.listar_disponibles())

    def a_dict(self):
        return [producto._a_dict() for producto in self.__productos]

    def cargar_desde_dict(self, lista):
        self.__productos = [Producto._desde_dict(d) for d in lista]
