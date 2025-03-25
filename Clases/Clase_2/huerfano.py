import os
import time

pid = os.fork()

if pid > 0:
    print(f"Soy el proceso padre ({os.getpid()}), terminando antes que mi hijo")
    exit(0)  # El padre termina inmediatamente
else:
    time.sleep(5)  # El hijo sigue ejecutándose mientras su padre muere
    print(f"Soy el proceso hijo ({os.getpid()}), mi padre ahora es {os.getppid()}")
