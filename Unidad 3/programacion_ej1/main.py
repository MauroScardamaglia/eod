RUTA = "corredores.bin"

CORREDORSIZE = 53 # el primer byte es 1 si el campo esta ocupado
CANTIDADCORREDORES = 12000
FILESIZE = CORREDORSIZE * CANTIDADCORREDORES

def stringToBytes(string, length):
    b = string.encode("ascii", errors="replace")  # o "replace" para ? en no ASCII
    if len(b) > length:
        return b[:length]
    return b.ljust(length, b"\x00") # rellena con 0

def hashDni(dni):
    return int(dni[3:8]) % 12007 #uso los últimos 5 dígitos del dni y luego hago el módulo con el número primo más cercano a 12000. Las posiciones 12000-12006 siempre van a ser colisiones/overflow

class Corredor:
    def __init__(self, dni, nombre, sexo, edad, categoria):
        self.dni = dni.zfill(8)        
        self.nombre = nombre #30 bytes
        self.sexo = sexo #1 byte
        self.edad = edad if edad < 255 else 255
        self.categoria = categoria #1 bytes
        self.tiempoLlegada = "" #luego HH:MM:SS:MM
    
    def setTiempoLlegada(self, tiempoLlegada):
        self.tiempoLlegada = tiempoLlegada

    #devuelve 52 bytes
    def toBinary(self): 
        binario += stringToBytes(self.dni, 8)
        binario += stringToBytes(self.nombre, 30)
        binario += stringToBytes(self.sexo, 1)
        binario += self.edad.to_bytes(1, byteorder="big", signed=False)
        binario += stringToBytes(self.categoria, 1)
        binario += stringToBytes(self.tiempoLlegada, 11)
        return binario
        
#se le pasa un bloque de 53 bytes y devuelve un objeto Corredor con los datos correspondientes. 
#el bloque de bytes se asume que tiene el formato definido en toBinary() y que el primer byte es el campo de ocupado (1 para ocupado, 2 para eliminado, 0 para libre)
def toCorredor(binario):
    dni = binario[1:9].rstrip(b"\x00").decode("ascii")
    nombre = binario[9:39].rstrip(b"\x00").decode("ascii")
    sexo = binario[39:40].rstrip(b"\x00").decode("ascii")
    edad = int.from_bytes(binario[40:41], byteorder="big", signed=False)
    categoria = binario[41:42].rstrip(b"\x00").decode("ascii")
    tiempoLlegada = binario[42:53].rstrip(b"\x00").decode("ascii")
    corredor = Corredor(dni, nombre, sexo, edad, categoria)
    corredor.setTiempoLlegada(tiempoLlegada)
    return corredor


def iniciaArchivo():
    with open(ruta, "wb") as f:
        f.write(b"\x00" * FILESIZE)

# busca si existe el corredor con el dni dado, devuelve la posición del corredor en el archivo o -1 si no existe
# si no encuentra en la primera posición que devuelve el hash, sigue buscando mientras el campo de ocupado
# se mantenga en 1 o en 2 (ocupado o eliminado) y no se hayan recorrido los 12000 corredores posibles
def buscaCorredor(dni):
    with open(ruta, "rb") as f:
        posicionInicial = (hashDni(dni) * CORREDORSIZE) % FILESIZE
        paso = 13 # coprimo con 12007 para recorrer todo el archivo sin repetir posiciones
        posicion = posicionInicial
        i = 0

        f.seek(posicion)
        lectura = f.read(CORREDORSIZE)
        dniLeido = lectura[1:9].rstrip(b"\x00").decode("ascii")
        while dniLeido != dni and (i < CANTIDADCORREDORES) and lectura[0] != 0: # mientras no encuentre el dni, no se haya recorrido todo el archivo y el campo de ocupado no sea 0 (libre)
            i += 1
            posicion = (posicion + paso*CORREDORSIZE) % FILESIZE
            f.seek(posicion) # siguiente corredor
            lectura = f.read(CORREDORSIZE)
            dniLeido = lectura[1:9].rstrip(b"\x00").decode("ascii")
        if (lectura[0] != 1 and dniLeido != dni) or i >= CANTIDADCORREDORES:           
            return -1
        else:
            return posicion


#recibe de argumento un dni de un corredor a insertar, devuelve la posicion libre que encuentra 
#en el archivo correspondiente a ese dni, resolviendo las colisiones
#retorna la posicion a insertar en el archivo o -1 si no hay una posicion disponible (overflow)
def buscaLibre(dni):
    with open(ruta, "rb") as f:
        posicion = (hashDni(dni) * CORREDORSIZE) % FILESIZE 
        f.seek(posicion)
        lectura = f.read(1)
        i = 0
        paso = 13
        while lectura[0] == 1 and i < CANTIDADCORREDORES:
            i += 1
            posicion = (posicion + paso * CORREDORSIZE) % FILESIZE
            f.seek(posicion)
            lectura = f.read(1)
        
        if i < CANTIDADCORREDORES:
            return posicion
        else:
            return -1


#inserta un corredor en el archivo recibiendo un objeto corredor 
#retorna true o false segun la operacion se pudo realizar correctamente
def altaCorredor(corredor):
    posCorredor = buscaLibre(corredor.dni)
    if posCorredor >= 0:
        with open(ruta, "r+b") as f:
            f.seek(posCorredor)
            f.write(b"\x01" + corredor.toBinary())
        return True
    else:
        return False
         
#recibiendo un dni como parametro elimina un corredor del archivo
#retorna true o false segun la operacion se pudo realizar correctamente        
def bajaCorredor(dni):
    pos = buscaCorredor(dni)
    if pos != -1:
        with open(ruta, "r+b") as f:
            f.seek(pos)
            f.write(b"\x02") # marco el primer byte como 2 para indicar que el espacio esta libre y que fue eliminado
            return True
    else:
        return False

#modifica un corredor sobreescribiendolo con los atributos del corredor recibido como parametro
#retorna true o false segun la operacion se pudo realizar correctamente 
def modificaCorredor(corredor):
    pos = buscaCorredor(corredor.dni)
    if pos != -1:
        with open(ruta, "r+b") as f:
            f.seek(pos)
            binario = b"\x01" + corredor.toBinary() # el primer byte es 1 para indicar que el campo esta ocupado
            f.write(binario)
            return True
    else:
        return False


def cargaTiempo(dni, tiempoLlegada):
    pos = buscaCorredor(dni)
    if pos == -1:
        return False
    else:
        with open(ruta,"r+b") as f:
            f.seek(pos)
            binario = f.read(CORREDORSIZE)                        
            corredor = toCorredor(binario)
            corredor.setTiempoLlegada(tiempoLlegada)    
            binario = b"\x01" + corredor.toBinary()
            f.seek(pos)
            f.write(binario)
        return True

def listadoGeneral():
    print("Listado general")
    with open(ruta,"rb") as f:
        for i in range(CANTIDADCORREDORES):
            binario = f.read(CORREDORSIZE)
            if binario[0] == 1:
                corredor = toCorredor(binario)
                print("DNI: ",corredor.dni)
                print("Nombre: ",corredor.nombre)
                print("Categoría (A = 21km, B = 42km): ",corredor.categoria)
                print("Tiempo: ",corredor.tiempoLlegada)
                print()

def listadoCategoria(categoria):
    print("Listado por categoría: ",categoria)
    with open(ruta,"rb") as f:
        for i in range(CANTIDADCORREDORES):
            binario = f.read(CORREDORSIZE)
            if binario[0] == 1:
                if chr(binario[41]) == categoria:
                    corredor = toCorredor(binario)
                    print("DNI: ",corredor.dni)
                    print("Nombre: ",corredor.nombre)
                    print("Tiempo: ",corredor.tiempoLlegada)
                    print()       


#dado un dni busca el corredor correspondiente en el archivo y devuelve el objeto corredor leido
#si no lo encuentra retorna None
def leeCorredor(dni):
    pos = buscaCorredor(dni)
    if pos >= 0:
        with open(ruta, "rb") as f:
            f.seek(pos)
            corredor = toCorredor(f.read(CORREDORSIZE))
            return corredor
    else:
        return None
        
        
P1 = Corredor("49494949", "Mario Antogno de las rosas", "M", 254, "B")
P2 = Corredor("3", "Tutankamon", "H", 2000, "A")
P3 = Corredor("47141192", "Juana de Arco", "H", 19, "B")
P4 = Corredor("35272341243232131", "Rodrigo de Triana de las Flores del Atlantico Sur", "Hermafrodita", 30, "Esta")
lista = [P1, P2, P3, P4]