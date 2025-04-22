# lector2.py
import os

fifo_path = 'mi_fifo'

with open(fifo_path, 'r') as fifo:
    datos = fifo.read()
    print("[Lector 2] Recibido:", datos)
