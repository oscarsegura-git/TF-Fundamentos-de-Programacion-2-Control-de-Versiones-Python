from clientes.cliente import Cliente
from comun.excepciones import ClienteDuplicadoError, ClienteNoEncontradoError

class GestorClientes:
    def __init__(self):
        self.__clientes = []

    def _indice(self, dni):
        dni = str(dni).strip()
        for i in range(len(self.__clientes)):
            if self.__clientes[i].dni == dni:
                return i
        return -1

    def existe(self, dni):
        return self._indice(dni) >= 0

    def registrar(self, dni, nombre, telefono, direccion, ciudad, distrito):
        cliente = Cliente(dni, nombre, telefono, direccion, ciudad, distrito)
        if self.existe(cliente.dni):
            raise ClienteDuplicadoError(
                "Ya existe un cliente registrado con el DNI " + cliente.dni + ".")
        self.__clientes.append(cliente)
        return cliente

    def buscar(self, dni):
        indice = self._indice(dni)
        if indice < 0:
            raise ClienteNoEncontradoError(
                "No existe un cliente con el DNI " + str(dni).strip() + ".")
        return self.__clientes[indice]

    def buscar_por_texto(self, texto):
        encontrados = [c for c in self.__clientes if c.coincide(texto)]
        if not encontrados:
            raise ClienteNoEncontradoError(
                "No se encontraron clientes para '" + str(texto).strip() + "'.")
        return encontrados

    def listar(self):
        return list(self.__clientes)

    def cantidad(self):
        return len(self.__clientes)

    def a_dict(self):
        return [cliente._a_dict() for cliente in self.__clientes]

    def cargar_desde_dict(self, lista):
        self.__clientes = [Cliente._desde_dict(d) for d in lista]

