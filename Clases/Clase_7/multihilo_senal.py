import signal
import threading
import time
import queue
import os

# Cola para comunicar señal al hilo
cola = queue.Queue()

def handler_usr1(signum, frame):
    print(f"[MAIN] Señal SIGUSR1 recibida. Enviando evento a hilo secundario...")
    cola.put("interrumpir")

def hilo_secundario():
    print("[HILO] Esperando evento del hilo principal...")
    while True:
        try:
            evento = cola.get(timeout=1)
            if evento == "interrumpir":
                print("[HILO] Recibida orden desde señal. Haciendo algo útil...")
        except queue.Empty:
            print("[HILO] Trabajando normalmente...")

# Registrar handler (solo el hilo principal lo hará)
signal.signal(signal.SIGUSR1, handler_usr1)

# Lanzar hilo secundario
t = threading.Thread(target=hilo_secundario, daemon=True)
t.start()

print(f"[MAIN] PID: {os.getpid()} - Esperando señales (kill -USR1 <pid>)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[MAIN] Terminando.")
