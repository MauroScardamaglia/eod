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
CANTIDADEMPLEADOS = 1000 # si se considera una empresa mediana a grande, 10000 considerando varias sucursales no es poco, este valor es muy relativo de todos modos
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

    # toString
    def __str__(self):
        return f"Empleado: {self.nombre} {self.apellido}, Dirección: {self.direccion}, Teléfono: {self.telefono}, Fecha de Ingreso: {self.fechaIngreso}"

#devuelve un hash de 2 bytes (16 bits) a partir del apellido y nombre del empleado, para usarlo como clave en la tabla hash, no hace modulo cantidad empleados
def hashEmpleado(apellido, nombre):
    # Usamos el apellido y nombre para generar la clave de hash
    clave = (apellido + nombre).lower()  # Convertimos a string minúsculas para consistencia
    if len(clave) % 2 != 0:
        clave += '\0'  # Si la longitud es impar, añadimos un byte nulo para completar el par  
    i = 0
    hash_value = 0
    while i < len(clave):
        hash_value = hash_value ^ (ord(clave[i])<<8 | ord(clave[i+1]))  # XOR de cada par de caracteres
        i += 2 
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



def insertarOverflow(binario):
    with open(RUTA, "ab") as f:
        f.write(binario)
        return True


def insertar(empleado):
    with open(RUTA, "r+b") as f:
        pos = hashEmpleado(empleado.apellido, empleado.nombre) % CANTIDADEMPLEADOS 
        pos *= EMPLEADOSIZE # para ir al byte correcto del archivo
        f.seek(pos)
        binario = f.read(EMPLEADOSIZE)
        nuevoBinario = b"\x01" + empleado.toBinary() # el byte de marcado va a ser 1 para indicar que el espacio está ocupado
        if binario[0] != 1:
            f.seek(pos)
            f.write(nuevoBinario)
            return True
        else:
            f.close()
            return insertarOverflow(nuevoBinario)

#retorna None si no encuentra elempleado
def consulta(apellido, nombre):
    pos = encuentroPosicion(apellido, nombre)
    if pos != -1:
        with open(RUTA, "rb") as f:
            f.seek(pos)
            binario = f.read(EMPLEADOSIZE)
            return toEmpleado(binario)

    else:
        return None

def eliminar(apellido, nombre):
    pos = encuentroPosicion(apellido, nombre)
    if pos != -1:
        with open(RUTA, "r+b") as f:
            f.seek(pos)
            f.write(b"\x02") # marco el byte de marcado como 2 para indicar que el espacio está libre y fue borrado
        return True
    else:
        return False
    
def modificar(nuevoEmpleado):
    pos = encuentroPosicion(nuevoEmpleado.apellido, nuevoEmpleado.nombre)
    if pos != -1:
        with open(RUTA, "r+b") as f:
            f.seek(pos)
            f.write(b"\x01"+nuevoEmpleado.toBinary()) # escribo el nuevo empleado en la misma posición, manteniendo el byte de marcado como 1
        return True
    else:
        return False

def encuentroPosicionOverflow(apellido, nombre):
    with open(RUTA, "rb") as f:
        f.seek(INITIALFILESIZE) # comienzo del área de overflow
        pos = INITIALFILESIZE
        while True:
            binario = f.read(EMPLEADOSIZE)
            if not binario:
                break
            if binario[0] == 1:
                empleado = toEmpleado(binario)
                if empleado.apellido.lower() == apellido.lower() and empleado.nombre.lower() == nombre.lower():
                    return pos
            pos += EMPLEADOSIZE
    return -1
        
def encuentroPosicion(apellido, nombre):
    pos = hashEmpleado(apellido, nombre) % CANTIDADEMPLEADOS
    pos *= EMPLEADOSIZE
    with open(RUTA, "rb") as f:
        f.seek(pos)
        binario = f.read(EMPLEADOSIZE)
        if binario[0] != 0:
            empleado = toEmpleado(binario)
            if empleado.apellido.lower() == apellido.lower() and empleado.nombre.lower() == nombre.lower() and binario[0] == 1:
                return pos
            else:
                f.close()
                return encuentroPosicionOverflow(apellido, nombre)
        else:
            return -1

iniciaArchivo()

empleado1 = Empleado("Licantropo", "Licantropo", "Av Siempreviva 742", "22342056", "01/01/2020")
empleado2 = Empleado("Gomez", "Juani", "Calle Falsa 123", "2231234567", "15/03/2019")
empleado3 = Empleado("Lope", "Pelo", "Calle Real 456", "2239876543", "30/06/2021")
empleado4 = Empleado("GoGo", "Meme", "Calle Falsa 123", "2231234567", "15/03/2019") # mismo nombre y apellido que empleado2 para probar colision
empleado5 = Empleado("Martuin", "Sexual", "Calle Falsa 123", "2231234567", "15/03/2019") # mismo nombre y apellido que empleado2 para probar colision
empleado6 = Empleado("Mama", "Pepe", "Calle Falsa 123", "2231234567", "15/03/2019") # mismo nombre y apellido que empleado2 para probar colision
empleado7 = Empleado("Sasa", "Mamalolo", "Calle Falsa 123", "2231234567", "15/03/2019") # mismo nombre y apellido que empleado2 para probar colision
conjuntoEmpleados = [empleado1, empleado2, empleado3, empleado4, empleado5, empleado6, empleado7]
for empleado in conjuntoEmpleados:
    if insertar(empleado):
        print(f"Empleado {empleado.nombre} {empleado.apellido} insertado correctamente.")
    else:
        print(f"Error al insertar el empleado {empleado.nombre} {empleado.apellido}.")

for empleado in conjuntoEmpleados:
    resultado = consulta(empleado.apellido, empleado.nombre)
    if resultado:
        print(f"Empleado encontrado: {resultado.nombre} {resultado.apellido}, Dirección: {resultado.direccion}, Teléfono: {resultado.telefono}, Fecha de Ingreso: {resultado.fechaIngreso}")
    else:
        print(f"Empleado {empleado.nombre} {empleado.apellido} no encontrado.")
