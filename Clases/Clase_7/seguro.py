# handler seguro

import signal
import time
import os

# Bandera para controlar el flujo
debe_terminar = False

def handler_usr1(signum, frame):
    global debe_terminar
    debe_terminar = True  # solo seteamos flag, no hacemos lógica compleja

# Asociar handler
signal.signal(signal.SIGUSR1, handler_usr1)

print(f"[PID {os.getpid()}] Esperando señal para terminar de forma segura...")

while True:
    print("[PROCESO] Trabajando...")
    time.sleep(1)

    if debe_terminar:
        print("[PROCESO] Señal recibida. Cerrando recursos y finalizando...")
        break
