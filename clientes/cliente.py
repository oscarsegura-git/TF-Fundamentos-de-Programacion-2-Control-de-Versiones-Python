from comun.excepciones import DniInvalidoError

class Cliente:
    def __init__(self, dni, nombre, telefono, direccion, ciudad, distrito):
        self.__dni = dni
        self.__nombre = nombre
        self.__telefono = telefono
        self.__direccion = direccion
        self.__ciudad = ciudad
        self.__distrito = distrito

    @property
    def dni(self):
        return self.__dni

    @dni.setter
    def dni(self, valor):
        valor = str(valor).strip()
        if not (len(valor) == 8 and valor.isdigit()):
            raise DniInvalidoError(
                "El DNI debe tener exactamente 8 digitos numericos.")
        self._dni = valor

    def resumen(self):
        return self.dni + " - " + self.nombre

    def __str__(self):
        return self.resumen()
