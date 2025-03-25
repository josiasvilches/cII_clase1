import os
import time

def atencion_clientes(n):
    pid = os.fork()
    if pid == 0:
        print(f"Soy el cliente {n} ({os.getpid()})")
        time.sleep(5)
        print(f"Cliente {n} terminando")
        os._exit(0)

# Simulación de servidor
cliente = 0
while cliente < 10:  # Limitar a 10 clientes por ahora
    atencion_clientes(cliente)
    cliente += 1
    time.sleep(1)  # Espera entre clientes

# Esperar que todos los hijos terminen
for _ in range(cliente):
    os.wait()
