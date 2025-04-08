# este codigo es similar al pipeline pero reemplaza las vocales por x, luego pone las palabras en mayúscula
import os

def hijo1(pipe1, pipe2):
    print("[hijo1] Iniciado")
    os.close(pipe1[1])   # Cierra escritura de pipe1
    os.close(pipe2[0])   # Cierra lectura de pipe2

    with os.fdopen(pipe1[0], 'r') as entrada, os.fdopen(pipe2[1], 'w') as salida:
        for linea in entrada:
            print(f"[hijo1] Leyó: {linea.strip()}")
            vocales = {'a': 'x', 'e': 'x', 'i': 'x', 'o': 'x', 'u': 'x',
           'A': 'x', 'E': 'x', 'I': 'x', 'O': 'x', 'U': 'x'}
            linea_modificada = ''.join(vocales.get(c, c) for c in linea)
            salida.write(linea_modificada.upper())

    print("[hijo1] Finalizado")
    os._exit(0)

def hijo2(pipe2, pipe1):
    print("[hijo2] Iniciado")
    os.close(pipe2[1])   # Cierra escritura de pipe2
    os.close(pipe1[0])   # Cierra lectura heredada de pipe1
    os.close(pipe1[1])   # Cierra escritura heredada de pipe1

    with os.fdopen(pipe2[0], 'r') as entrada:
        for linea in entrada:
            print(f"Hijo 2 imprime: {linea.strip()}")

    print("[hijo2] Finalizado")
    os._exit(0)

def main():
    print("[padre] Iniciado")
    pipe1 = os.pipe()  # padre → hijo1
    pipe2 = os.pipe()  # hijo1 → hijo2

    pid1 = os.fork()
    if pid1 == 0:
        hijo1(pipe1, pipe2)

    pid2 = os.fork()
    if pid2 == 0:
        hijo2(pipe2, pipe1)

    # Proceso padre
    os.close(pipe1[0])  # Cierra lectura de pipe1
    os.close(pipe2[0])  # No usa pipe2
    os.close(pipe2[1])  # No usa pipe2

    with os.fdopen(pipe1[1], 'w') as salida:
        nombres = ["marcos", "lucia", "daniel", "emma"]
        for nombre in nombres:
            print(f"[padre] Enviando: {nombre}")
            salida.write(nombre + "\n")

    print("[padre] Finalizado escritura")

    os.wait()
    os.wait()
    print("[padre] Finalizado")

if __name__ == "__main__":
    main()
