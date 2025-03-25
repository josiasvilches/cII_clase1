import os
import time

pid = os.fork()

if pid > 0:
    print(f"Soy el proceso padre ({os.getpid()}), mi hijo es {pid}")
    time.sleep(10)  # Simulamos que el padre está ocupado y no recoge el estado del hijo
else:
    print(f"Soy el proceso hijo ({os.getpid()}), terminando mi ejecución")
    exit(0)  # El hijo termina inmediatamente
