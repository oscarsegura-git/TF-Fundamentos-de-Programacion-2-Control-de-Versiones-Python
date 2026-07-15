from pedidos.pedido import COMPRADO, EN_TRANSITO, EN_ALMACEN

def cargar(gestor_clientes, gestor_productos, gestor_pedidos):
    gestor_clientes.registrar("72345678", "Valeria Quispe Mamani", "987654321",
                              "Jr. Los Pinos 234", "Lima", "San Juan de Lurigancho")
    gestor_clientes.registrar("45321789", "Jorge Mamani Condori", "954321789",
                              "Av. Grau 456", "Arequipa", "Cercado")
    gestor_clientes.registrar("61234890", "Lucía Torres Díaz", "912345678",
                              "Av. Primavera 100", "Lima", "Surco")

    gestor_productos.registrar("P001", "Vestido floral manga larga", "Ropa femenina", 65.00)
    gestor_productos.registrar("P002", "Blusa oversize rayas", "Ropa femenina", 38.00)
    gestor_productos.registrar("P003", "Labial SHEGLAM mate rojo", "Cosméticos", 22.00)
    gestor_productos.registrar("P004", "Bolso bandolera", "Accesorios", 55.00)
    gestor_productos.registrar("P005", "Paca mixta 10 prendas", "Pacas", 180.00)
    gestor_productos.desactivar("P004")

    pedido1 = gestor_pedidos.registrar("72345678", "Ropa femenina", 2, 1.5)
    pedido2 = gestor_pedidos.registrar("45321789", "Accesorios", 1, 1.2)
    for pedido in [pedido1, pedido2]:
        pedido.cambiar_estado(COMPRADO)
        pedido.cambiar_estado(EN_TRANSITO)
        pedido.cambiar_estado(EN_ALMACEN)

    gestor_pedidos.registrar("61234890", "Cosméticos", 3, 0.8)
