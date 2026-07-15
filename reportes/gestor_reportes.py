from comun import recursos
from comun.excepciones import EntregaNoDisponibleError

class GestorReportes:
    def __init__(self, gestor_pedidos):
        self.__gestor_pedidos = gestor_pedidos

    def costo_envio(self, pedido):
        if pedido.entrega is None:
            raise EntregaNoDisponibleError(
                "El pedido no tiene una entrega asignada.")
        return pedido.entrega.desglose()

    def filtrar(self, estado=None, dni=None, desde=None, hasta=None):
        pedidos = self.__gestor_pedidos.listar()
        if estado:
            pedidos = [p for p in pedidos if p.estado == estado]
        if dni:
            pedidos = [p for p in pedidos if p.cliente.dni == str(dni).strip()]
        if desde and hasta:
            pedidos = [p for p in pedidos
                       if desde <= p.fecha_registro.date() <= hasta]
        return pedidos

    def total_periodo(self, pedidos):
        total = 0.0
        for pedido in pedidos:
            if pedido.entrega is not None:
                total += pedido.entrega.desglose()[2]
        return total

    def exportar_excel(self, pedidos, nombre_archivo):
        encabezados = ["Código pedido", "Cliente", "DNI", "Tipo prenda",
                       "Peso (kg)", "Estado", "Tipo entrega", "Costo envío (S/)",
                       "Total c/IGV (S/)", "Última actualización", "Comprobante",
                       "Vista previa"]
        columna_imagen = len(encabezados)
        filas = []
        imagenes = []
        fila_excel = 1
        for pedido in pedidos:
            fila_excel += 1
            if pedido.entrega is None:
                tipo_entrega = "Sin entrega"
                costo = 0.0
                total = 0.0
                comprobante = "-"
            else:
                tipo_entrega = pedido.entrega.descripcion()
                costo, _, total = pedido.entrega.desglose()
                comprobante = pedido.entrega.comprobante_archivo or "-"
                if comprobante.lower().endswith(".png"):
                    imagenes.append([comprobante, fila_excel, columna_imagen])
            filas.append([
                pedido.codigo, pedido.cliente.nombre, pedido.cliente.dni,
                pedido.tipo_prenda, pedido.peso, pedido.estado, tipo_entrega,
                round(costo, 2), round(total, 2), pedido.ultima_actualizacion(),
                comprobante, "",
            ])
        return recursos.exportar_excel(nombre_archivo, encabezados, filas, imagenes)
