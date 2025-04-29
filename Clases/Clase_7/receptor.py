import signal
import time
import os

interrupciones = 0
max_interrupciones = 5

def handler_usr1(signum, frame):
    global interrupciones
    interrupciones += 1
    print(f"[PID {os.getpid()}] Señal SIGUSR1 recibida!. Interrupciones: {interrupciones}")
    if interrupciones >= max_interrupciones:
        print(f"[PID {os.getpid()}] Límite alcanzado. Terminando proceso.")
        exit(0)

# Registrar handler
signal.signal(signal.SIGUSR1, handler_usr1)

print(f"[INFO] Esperando señales... PID: {os.getpid()}")
while True:
    print("Trabajando... (kill -USR1 <pid> para interrumpir)")
    time.sleep(1)
