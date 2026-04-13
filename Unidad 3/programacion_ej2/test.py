direccion = "prueba.bin"
with open(direccion, "wb") as f:
    f.write(b"\x00" * 100) # escribe 100 bytes de 0 en el archivo, para inicializarlo

#ahora voy a hacer un append
with open(direccion, "ab") as f:
    f.write(b"Hola Mundo") # escribe "Hola Mundo" al final del archivo

with open(direccion, "r+b") as f:
    f.seek(100)
    #voy a leer caracter a caracter hasta llegar al final del archivo
    while True:
        byte = f.read(1)
        if not byte:
            break
        print(byte.decode("ascii"), end="") # decodifico el byte a ascii y lo imprimo sin salto de linea
