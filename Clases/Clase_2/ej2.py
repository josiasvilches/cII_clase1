# Crear un proceso huérfano y confirmar que init o systemd lo adoptan.
import os
import time

pid = os.fork()

if pid > 0:
    print(f"Soy el proceso padre ({os.getpid()}), terminando antes que mi hijo")
    exit(0)  # El padre termina inmediatamente
else:
    time.sleep(15)  # El hijo sigue ejecutándose mientras su padre muere
    print(f"Soy el proceso hijo ({os.getpid()}), mi padre ahora es {os.getppid()}")
