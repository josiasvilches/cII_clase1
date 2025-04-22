import os
import time
from funciones_fifo import read_fifo, write_fifo

fifo_lectura_path = "mi_fifo"  # FIFO donde va a leer
fifo_escritura_path = "mi_fifo1"  # FIFO donde va a escribir

# Abrimos el FIFO para lectura
fifo_r = open(fifo_lectura_path, 'r')

# Abrimos el FIFO para escritura
fifo_w = open(fifo_escritura_path, 'w')  # Cambié os.open por open aquí

try:
    while True:
        # Mensaje para enviar
        entrada = input("Escribe un mensaje para el otro proceso: ")

        # Aquí es donde escribe en el FIFO
        write_fifo(fifo_w, entrada)

        # Mostramos lo que escribimos
        print(f"Escribiendo en FIFO: {entrada}")

        if entrada == "":
            print("Cerrando el chat.")
            break

        # Tiempo para dar chance al otro proceso de leer
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nInterrumpido con Ctrl+C. Cerrando.")

finally:
    fifo_r.close()
    fifo_w.close()
