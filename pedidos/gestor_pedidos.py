from datetime import datetime

from pedidos.pedido import Pedido
from comun.excepciones import PedidoNoEncontradoError

class GestorPedidos:
    def __init__(self, gestor_clientes):
        self.__gestor_clientes = gestor_clientes
        self.__pedidos = []
        self.__contador = 0

    def _indice(self, codigo):
        codigo = str(codigo).strip().upper()
        for i in range(len(self.__pedidos)):
            if self.__pedidos[i].codigo == codigo:
                return i
        return -1

    def _generar_codigo(self):
        fecha = datetime.now().strftime("%Y%m%d")
        while True:
            self.__contador += 1
            codigo = "TSP-" + fecha + "-" + str(self.__contador).zfill(4)
            if self._indice(codigo) < 0:
                return codigo

    def registrar(self, dni_cliente, tipo_prenda, cantidad, peso):
        cliente = self.__gestor_clientes.buscar(dni_cliente)
        pedido = Pedido(self._generar_codigo(), cliente, tipo_prenda, cantidad, peso)
        self.__pedidos.append(pedido)
        return pedido

    def buscar_por_codigo(self, codigo):
        indice = self._indice(codigo)
        if indice < 0:
            raise PedidoNoEncontradoError(
                "No existe un pedido con el código " +
                str(codigo).strip().upper() + ".")
        return self.__pedidos[indice]

    def buscar(self, texto):
        encontrados = [p for p in self.__pedidos if p.coincide(texto)]
        if not encontrados:
            raise PedidoNoEncontradoError(
                "No se encontraron pedidos para '" + str(texto).strip() + "'.")
        return encontrados

    def pedidos_de_cliente(self, dni):
        dni = str(dni).strip()
        return [p for p in self.__pedidos if p.cliente.dni == dni]

    def listar(self):
        return list(self.__pedidos)

    def a_dict(self):
        return [pedido._a_dict() for pedido in self.__pedidos]

    def cargar_desde_dict(self, lista, gestor_clientes, gestor_productos):
        from entregas.entrega import entrega_desde_dict
        pedidos = []
        contador = 0
        for datos_pedido in lista:
            try:
                cliente = gestor_clientes.buscar(datos_pedido["cliente_dni"])
            except Exception:
                continue
            pedido = Pedido._desde_dict(datos_pedido, cliente, gestor_productos.buscar)
            entrega_data = datos_pedido.get("entrega")
            if entrega_data:
                pedido.asignar_entrega(entrega_desde_dict(entrega_data))
            pedidos.append(pedido)
            try:
                numero = int(pedido.codigo.split("-")[-1])
                contador = max(contador, numero)
            except (ValueError, IndexError):
                pass
        self.__pedidos = pedidos
        self.__contador = contador
