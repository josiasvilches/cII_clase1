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

# hijo 1 -> 3 segundos, hijo 2 -> 5 segundos (soy hijo mi PID es ............), que el padre no haga wait y al finalizar diga soy el padre mi pid es ....