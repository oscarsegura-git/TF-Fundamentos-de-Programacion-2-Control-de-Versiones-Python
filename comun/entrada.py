from datetime import datetime

from comun.excepciones import DatoInvalidoError

def pedir_texto(mensaje, obligatorio=True):
    while True:
        texto = input(mensaje).strip()
        try:
            if obligatorio and texto == "":
                raise DatoInvalidoError("El campo no puede estar vacio.")
            return texto
        except DatoInvalidoError as error:
            print("  [ERROR] " + str(error) + " Ingrese nuevamente.")

def pedir_entero(mensaje, minimo=1):
    while True:
        try:
            numero = int(input(mensaje))
            if numero < minimo:
                raise DatoInvalidoError("El valor debe ser mayor o igual a " + str(minimo) + ".")
            return numero
        except ValueError:
            print("  [ERROR] Debe ingresar un numero entero. Ingrese nuevamente.")
        except DatoInvalidoError as error:
            print("  [ERROR] " + str(error) + " Ingrese nuevamente.")

def pedir_decimal(mensaje, minimo=0.0, estricto=True):
    while True:
        try:
            numero = float(input(mensaje))
            if estricto and numero <= minimo:
                raise DatoInvalidoError("El valor debe ser mayor que " + str(minimo) + ".")
            if not estricto and numero < minimo:
                raise DatoInvalidoError("El valor no puede ser menor que " + str(minimo) + ".")
            return numero
        except ValueError:
            print("  [ERROR] Debe ingresar un numero. Ingrese nuevamente.")
        except DatoInvalidoError as error:
            print("  [ERROR] " + str(error) + " Ingrese nuevamente.")

def pedir_fecha(mensaje):
    while True:
        fecha = input(mensaje).strip()
        try:
            datetime.strptime(fecha, "%Y-%m-%d %H:%M")
            return fecha
        except ValueError:
            print("  [ERROR] Use el formato AAAA-MM-DD HH:MM. Ingrese nuevamente.")

def pedir_opcion(mensaje, opciones_validas):
    validas = [str(o) for o in opciones_validas]
    while True:
        opcion = input(mensaje).strip()
        if opcion in validas:
            return opcion
        print("  [ERROR] Opcion no valida. Elija entre: " + ", ".join(validas) + ".")

def pausar():
    input("\n Presione Enter para continuar...")

def linea():
    return "-" * 54
