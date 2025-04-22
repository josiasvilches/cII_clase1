import os

fifo_path = 'mi_fifo'

with open(fifo_path, 'r') as fifo:
    print("Esperando mensaje...")
    mensaje = fifo.read()
    print("Mensaje recibido:", mensaje)
