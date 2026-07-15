class SGPError(Exception):
    pass

class DatoInvalidoError(SGPError):
    pass

class DniInvalidoError(DatoInvalidoError):
    pass

class ClienteDuplicadoError(SGPError):
    pass

class ClienteNoEncontradoError(SGPError):
    pass

class ProductoDuplicadoError(SGPError):
    pass

class ProductoNoEncontradoError(SGPError):
    pass

class PedidoNoEncontradoError(SGPError):
    pass

class TransicionInvalidaError(SGPError):
    pass

class EntregaNoDisponibleError(SGPError):
    pass

