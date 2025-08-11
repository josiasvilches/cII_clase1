# que un padre tenga un hijo y así por 3/4 generaciones

import os
import time

def generaciones(n):
    pid = os.fork()
    if pid > 0:
        print(f"Soy el padre ({os.getpid()}) y tengo un hijo con PID {pid}")
        os.wait()
    else:
        if n > 0:
            print(f"Soy el hijo ({os.getpid()}) y voy a crear otro hijo")
            generaciones(n - 1)
        else:
            print(f"Soy el hijo terminal ({os.getpid()}) y no tengo más hijos")
        time.sleep(3)
        print(f"Soy el hijo ({os.getpid()}) y estoy terminando")
        os._exit(0)

hijo = 0
while hijo < 3:  # Limitar a 3 generaciones por ahora
    generaciones(hijo)
    hijo += 1
    time.sleep(1)  # Espera entre generaciones

for _ in range(hijo):
    os.wait()
