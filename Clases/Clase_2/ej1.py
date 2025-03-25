# Modificar el código para evitar procesos zombis correctamente con os.wait()
import os
import time

pid = os.fork()

if pid > 0:
    print(f"Soy el proceso padre ({os.getpid()}), esperando a mi hijo ({pid})")
    time.sleep(5)  # Simulamos trabajo del padre
    # Falta una línea para evitar el zombi
    os.wait()
else:
    print(f"Soy el proceso hijo ({os.getpid()}), terminando mi ejecución")
    exit(0)
