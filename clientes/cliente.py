from comun.excepciones import DatoInvalidoError, DniInvalidoError

class Cliente:
    def __init__(self, dni, nombre, telefono, direccion, ciudad, distrito):
        self.__dni = self._validar_dni(dni)
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion
        self.ciudad = ciudad
        self.distrito = distrito

    def _validar_dni(self, valor):
        valor = str(valor).strip()
        if not (len(valor) == 8 and valor.isdigit()):
            raise DniInvalidoError(
                "El DNI debe contener exactamente 8 dígitos numéricos.")
        return valor

    def _validar_texto(self, valor, campo):
        valor = str(valor).strip()
        if valor == "":
            raise DatoInvalidoError("El campo " + campo + " no puede estar vacío.")
        return valor

    @property
    def dni(self):
        return self.__dni

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = self._validar_texto(valor, "nombre")

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = self._validar_texto(valor, "teléfono")

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = self._validar_texto(valor, "dirección")

    @property
    def ciudad(self):
        return self.__ciudad

    @ciudad.setter
    def ciudad(self, valor):
        self.__ciudad = self._validar_texto(valor, "ciudad")

    @property
    def distrito(self):
        return self.__distrito

    @distrito.setter
    def distrito(self, valor):
        self.__distrito = self._validar_texto(valor, "distrito")

    def direccion_completa(self):
        return self.__direccion + ", " + self.__distrito + ", " + self.__ciudad

    def coincide(self, texto):
        texto = str(texto).strip().lower()
        return texto == self.__dni or texto in self.__nombre.lower()

    def __str__(self):
        return self.__dni + " - " + self.__nombre

    def _a_dict(self):
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "distrito": self.distrito,
        }

    @classmethod
    def _desde_dict(cls, data):
        return cls(data["dni"], data["nombre"], data["telefono"],
                   data["direccion"], data["ciudad"], data["distrito"])
