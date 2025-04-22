import os
import time
from funciones_fifo import read_fifo, write_fifo

fifo_lectura_path = "mi_fifo1"  # FIFO donde va a leer
fifo_escritura_path = "mi_fifo"  # FIFO donde va a escribir

# Abrimos el FIFO para lectura (modo no bloqueante)
fd_r = os.open(fifo_lectura_path, os.O_RDONLY | os.O_NONBLOCK)
fifo_r = os.fdopen(fd_r, 'r')

# Abrimos el FIFO para escritura
fifo_w = open(fifo_escritura_path, 'w')

try:
    while True:
        print("Esperando mensaje...")
        mensaje = ""

        # Intentamos recibir algo con pequeños descansos
        for _ in range(50):  # 50 intentos, 5 segundos
            mensaje = read_fifo(fifo_r)
            if mensaje != "":
                break
            time.sleep(0.1)

        if mensaje == "":
            print("No llegó ningún mensaje. ¿Está corriendo el otro proceso?")
            continue

        print("Mensaje recibido:", mensaje)

        # Después de recibir el mensaje, respondemos
        entrada = input("Tu mensaje: ")

        # Aquí se escribe el mensaje en el FIFO
        write_fifo(fifo_w, entrada)

        if entrada == "":
            print("Cerrando el chat.")
            break

except KeyboardInterrupt:
    print("\nInterrumpido con Ctrl+C. Cerrando.")

finally:
    fifo_r.close()
    fifo_w.close()
