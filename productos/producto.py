from comun.excepciones import DatoInvalidoError

CATEGORIAS = ["Ropa femenina", "Ropa masculina", "Accesorios", "Cosméticos", "Pacas"]

class Producto:
    def __init__(self, codigo, nombre, categoria, precio):
        self.__codigo = str(codigo).strip().upper()
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.__activo = True

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor).strip()
        if valor == "":
            raise DatoInvalidoError("El nombre del producto no puede estar vacío.")
        self.__nombre = valor

    @property
    def categoria(self):
        return self.__categoria

    @categoria.setter
    def categoria(self, valor):
        if valor not in CATEGORIAS:
            raise DatoInvalidoError(
                "Categoría no válida. Opciones: " + ", ".join(CATEGORIAS) + ".")
        self.__categoria = valor

    @property
    def precio(self):
        return self.__precio

    @precio.setter
    def precio(self, valor):
        if valor <= 0:
            raise DatoInvalidoError("El precio debe ser un valor positivo.")
        self.__precio = float(valor)

    @property
    def activo(self):
        return self.__activo

    def activar(self):
        self.__activo = True

    def desactivar(self):
        self.__activo = False

    def estado_texto(self):
        return "Activo" if self.__activo else "Inactivo"

    def coincide(self, texto):
        texto = str(texto).strip().lower()
        return texto == self.__codigo.lower() or texto in self.__nombre.lower()

    def __str__(self):
        return self.__codigo + " - " + self.__nombre + " (S/ " + \
            format(self.__precio, ".2f") + ")"

    def _a_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "activo": self.activo,
        }

    @classmethod
    def _desde_dict(cls, data):
        producto = cls(data["codigo"], data["nombre"], data["categoria"], data["precio"])
        if not data.get("activo", True):
            producto.desactivar()
        return producto
