'''
    apellido 20 bytes?
	nombre 15 bytes?
	direccion (av Siempreviva 742 (18)) 30 bytes San Carlos de Bariloche 586 (27) con 30 bytes alcanza si es una dirección local, si hay que poner ciudad, etc hay que añadir bytes (50?)
	telefono (ej 223 420 5623) 10 bytes
	fecha de ingreso (dd/mm/aa) 10 bytes
    Sumatoria = 85 bytes
    + 1 marcado en archivo -> 86
    
    hacer nombre + apellido? o hacer nombre completo ? (por tema clave conviene la segunda creo yo)
'''

RUTA = "empleados.bin"
EMPLEADOSIZE = 86 # considerando el byte de marcado, es para el archivo
CANTIDADEMPLEADOS = 10000 # si se considera una empresa mediana a grande, 10000 considerando varias sucursales no es poco, este valor es muy relativo de todos modos
INITIALFILESIZE = EMPLEADOSIZE * CANTIDADEMPLEADOS

def stringToBytes(cadena, length):
    b = cadena.encode("ascii", errors="replace")  # o "replace" para ? en no ASCII
    if len(b) > length:
        return b[:length]
    return b.ljust(length, b"\x00") # rellena con 0 

class Empleado:
    def __init__(self, apellido, nombre, direccion, telefono, fechaIngreso):
        self.apellido = apellido #20 bytes
        self.nombre = nombre #15 bytes
        self.direccion = direccion #30 bytes
        self.telefono = telefono #10 bytes (cod area (2/3) + número (8/7))
        self.fechaIngreso = fechaIngreso #10 bytes (dd/mm/aaaa)
    
    #devuelve un binario de 85 bytes, para escribirlo se debe añadir un byte de marcado al principio, quedando 86 bytes para el archivo
    def toBinary(self):
        binario = stringToBytes(self.apellido,20)
        binario += stringToBytes(self.nombre, 15)
        binario += stringToBytes(self.direccion, 30)
        binario += stringToBytes(self.telefono, 10)
        binario += stringToBytes(self.fechaIngreso, 10)
        return binario 

#devuelve un hash de 2 bytes (16 bits) a partir del apellido y nombre del empleado, para usarlo como clave en la tabla hash, no hace modulo cantidad empleados
def hashEmpleado(empleado):
    # Usamos el apellido y nombre para generar la clave de hash
    clave = (empleado.apellido + empleado.nombre).lower()  # Convertimos a minúsculas para consistencia
    if len(clave) % 2 != 0:
        clave += "\0"  # Si la longitud es impar, añadimos un byte nulo para completar el par  
    i = 0
    hash_value = 0
    while i < len(clave)/2:
        hash_value = hash_value ^ clave[i:i+2].encode("ascii", errors="replace")  # XOR de cada par de caracteres
    return hash_value
        
# le llega un bloque de 86 bytes,omite el primero y lo convierte a string y lo devuelve como un objeto Empleado
def toEmpleado(binario):
    if len(binario) != EMPLEADOSIZE:
        raise ValueError("El bloque binario debe tener exactamente 86 bytes")
    # Omitir el primer byte (marcado)
    binario = binario[1:]
    
    apellido = binario[0:20].rstrip(b"\x00").decode("ascii", errors="replace")
    nombre = binario[20:35].rstrip(b"\x00").decode("ascii", errors="replace")
    direccion = binario[35:65].rstrip(b"\x00").decode("ascii", errors="replace")
    telefono = binario[65:75].rstrip(b"\x00").decode("ascii", errors="replace")
    fechaIngreso = binario[75:85].rstrip(b"\x00").decode("ascii", errors="replace")
    
    return Empleado(apellido, nombre, direccion, telefono, fechaIngreso)
    
def iniciaArchivo():
    with open(RUTA, "wb") as f:
    	f.write(b"\x00" * INITIALFILESIZE)
	# haciendo seek INITIALFILESIZE (o mas 1) llegas al comienzo del área separada de overflow


