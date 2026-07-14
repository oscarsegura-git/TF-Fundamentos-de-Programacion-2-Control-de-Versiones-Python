from clientes.cliente import Cliente
from comun.excepciones import ClienteDuplicadoError, ClienteNoEncontradoError

class GestorClientes:
    def __init__(self):
        self._clientes = {}

    def existe(self, dni):
        return str(dni).strip() in self._clientes

    def registrar(self, dni, nombre, telefono, direccion, ciudad, distrito):
        cliente = Cliente(dni, nombre, telefono, direccion, ciudad, distrito)
        if self.existe(cliente.dni):
            raise ClienteDuplicadoError(
                "Ya existe un cliente registrado con el DNI " + cliente.dni + ".")
        self._clientes[cliente.dni] = cliente
        return cliente

    def buscar(self, dni):
        dni = str(dni).strip()
        if dni not in self._clientes:
            raise ClienteNoEncontradoError(
                "No existe un cliente con el DNI " + dni + ".")
        return self._clientes[dni]

    def obtener_o_none(self, dni):
        return self._clientes.get(str(dni).strip())

    def actualizar(self, dni, nombre=None, telefono=None, direccion=None,
                   ciudad=None, distrito=None):
        cliente = self.buscar(dni)
        if nombre:
            cliente.nombre = nombre
        if telefono:
            cliente.telefono = telefono
        if direccion:
            cliente.direccion = direccion
        if ciudad:
            cliente.ciudad = ciudad
        if distrito:
            cliente.distrito = distrito
        return cliente

    def listar(self):
        return list(self._clientes.values())

    def cantidad(self):
        return len(self._clientes)
