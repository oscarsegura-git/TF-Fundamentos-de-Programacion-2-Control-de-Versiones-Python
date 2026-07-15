import json
import os

RUTA_DATOS = "datos_sistema.json"

def existen_datos(ruta=RUTA_DATOS):
    return os.path.exists(ruta) and os.path.getsize(ruta) > 0

def guardar(gestor_clientes, gestor_productos, gestor_pedidos, ruta=RUTA_DATOS):
    datos = {
        "clientes": gestor_clientes.a_dict(),
        "productos": gestor_productos.a_dict(),
        "pedidos": gestor_pedidos.a_dict(),
    }
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)

def cargar(gestor_clientes, gestor_productos, gestor_pedidos, ruta=RUTA_DATOS):
    if not existen_datos(ruta):
        return False
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return False
    gestor_clientes.cargar_desde_dict(datos.get("clientes", []))
    gestor_productos.cargar_desde_dict(datos.get("productos", []))
    gestor_pedidos.cargar_desde_dict(datos.get("pedidos", []), gestor_clientes,
                                     gestor_productos)
    return True
