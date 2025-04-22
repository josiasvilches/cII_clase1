import os

fifo_path = 'mi_fifo'

with open(fifo_path, 'w') as fifo:
    print("Escribiendo mensaje en FIFO...")
    fifo.write("¡Hola desde el proceso escritor!\n")
    print("Mensaje enviado.")
