import os
import time
import signal

# Reemplazá esto con el PID real del receptor
PID_RECEPTOR = int(input("Ingresá el PID del receptor: "))

try:
    while True:
        print(f"[EMISOR] Enviando SIGUSR1 a PID {PID_RECEPTOR}")
        os.kill(PID_RECEPTOR, signal.SIGUSR1)
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[EMISOR] Interrumpido por el usuario. Terminando.")
